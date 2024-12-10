import os
import time
import jwt
import requests
import re
from flask import Flask, request, jsonify
from git import Repo
import logging
import shutil

# Flask app setup
app = Flask(__name__)

# GitHub App Configuration
APP_ID = "1081952"  # Replace with your GitHub App ID
PRIVATE_KEY_PATH = "./private-key.pem"  # Replace with the path to your private key file

# Dockerfile vulnerability checks
general_checks = [
    # Base image security
    {"pattern": r"FROM .*:latest", 
     "description": "Avoid using 'latest' tag in base images.",
     "suggestion": "Pin the base image version (e.g., FROM python:3.9).",
     "owasp_category": "A6 - Using Components with Known Vulnerabilities"},

    # Privilege escalation prevention
    {"pattern": r"USER root", 
     "description": "Running as root is insecure.",
     "suggestion": "Use a non-root user.",
     "owasp_category": "A5 - Improper Privilege Management"},

    # Missing health monitoring
    # File-level check for HEALTHCHECK
    {"pattern": r"\bHEALTHCHECK\b", 
     "description": "Missing HEALTHCHECK instruction.",
     "suggestion": "Add a HEALTHCHECK instruction to monitor container health.",
     "owasp_category": "A10 - Insufficient Monitoring and Logging"},


    # Downloading remote files
    {"pattern": r"^ADD\s+(https?://)", 
     "description": "Avoid using ADD for fetching remote files.",
     "suggestion": "Use CURL or WGET instead of ADD to download files.",
     "owasp_category": "A6 - Using Components with Known Vulnerabilities"},

    # Using ADD when COPY suffices
    {"pattern": r"^ADD .*", 
     "description": "Avoid using ADD when COPY is sufficient.",
     "suggestion": "Use COPY instead of ADD unless extracting archives.",
     "owasp_category": "A5 - Improper Privilege Management"},

    # Exposing unnecessary ports
    {"pattern": r"^EXPOSE\s+(?!80|443)\d{1,5}", 
     "description": "Exposing unnecessary ports.",
     "suggestion": "Only expose port 80 (HTTP) or 443 (HTTPS), or justify the need for other ports.",
     "owasp_category": "A6 - Using Components with Known Vulnerabilities"},

    # Excessive permissions
    {"pattern": r"RUN chmod 777 .*", 
     "description": "Excessive file permissions granted.",
     "suggestion": "Avoid using chmod 777; use least privilege principles.",
     "owasp_category": "A5 - Improper Privilege Management"},

    # Hardcoded secrets
    {"pattern": r"ENV\s+\w+=.*", 
     "description": "Sensitive data in ENV variables.",
     "suggestion": "Avoid hardcoding secrets; use Docker secrets instead.",
     "owasp_category": "A3 - Sensitive Data Exposure"},

    # Files copied to root
    {"pattern": r"COPY .* /root", 
     "description": "Files copied to root directory.",
     "suggestion": "Avoid copying files to /root; use application-specific directories.",
     "owasp_category": "A5 - Improper Privilege Management"},

    # Deprecated instructions
    {"pattern": r"MAINTAINER .*", 
     "description": "Deprecated MAINTAINER instruction.",
     "suggestion": "Use LABEL for maintainer information instead.",
     "owasp_category": "A9 - Using Components with Known Vulnerabilities"},
]


# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s", filename="app.log", filemode="a")

# Helper: Generate JWT
def generate_jwt():
    """Generate a JWT for GitHub App authentication."""
    with open(PRIVATE_KEY_PATH, "r") as key_file:
        private_key = key_file.read()
    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,  # Token valid for 10 minutes
        "iss": APP_ID
    }
    return jwt.encode(payload, private_key, algorithm="RS256")

# Helper: Get Installation Access Token
def get_installation_access_token(jwt_token, installation_id):
    """Fetch an installation access token using the JWT."""
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    token_url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    response = requests.post(token_url, headers=headers)
    if response.status_code != 201:
        raise Exception(f"Failed to get access token: {response.text}")
    return response.json()["token"]

# Helper: Post results to GitHub Checks tab
def post_check_run(repo_full_name, head_sha, check_run_name, file_path, results, access_token):
    """Post the results as a check run to the GitHub repository."""
    check_url = f"https://api.github.com/repos/{repo_full_name}/check-runs"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    conclusion = "failure" if results else "success"

    # Format the output text from the results
    output_text = "\n".join([f"- {line}: {', '.join(issues)}" for line, issues in results.items()])
    if not output_text:
        output_text = "No vulnerabilities found."

    # Prepare data for the Check Run
    data = {
        "name": check_run_name,
        "head_sha": head_sha,
        "status": "completed",
        "conclusion": conclusion,
        "output": {
            "title": f"Dockerfile Scan - {os.path.basename(file_path)}",
            "summary": "Scan results for Dockerfile.",
            "text": output_text
        }
    }

    # Post the check run to GitHub
    response = requests.post(check_url, json=data, headers=headers)
    if response.status_code != 201:
        raise Exception(f"Failed to create check run: {response.text}")


# Perform checks based on platform
def check_vulnerabilities(file_content):
    """Scan Dockerfile content for vulnerabilities."""
    results = {}
    lines = file_content.splitlines()

    for line_num, line in enumerate(lines, start=1):
        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith("#"):
            continue

        line_issues = set()
        for check in general_checks:
            if re.search(check["pattern"], line):
                line_issues.add(f"{check['description']} (Suggestion: {check['suggestion']})")
        if line_issues:
            results[f"Line {line_num}"] = list(line_issues)

    return results


# Clone repository and scan
def clone_and_scan(repo_url, access_token):
    """Clone the repository and scan for Dockerfile vulnerabilities."""
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    repo_path = os.path.join(os.getcwd(), repo_name)

    # Clean up any previous clone
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path, ignore_errors=True)

    # Clone the repository
    token_url = repo_url.replace("https://", f"https://{access_token}@")
    Repo.clone_from(token_url, repo_path)

    # Scan all Dockerfiles inside 'apps' or any subdirectory
    results = {}
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file == "Dockerfile":
                file_path = os.path.join(root, file)
                logging.info(f"Found Dockerfile: {file_path}")
                with open(file_path, "r") as f:
                    file_content = f.read()
                vulnerabilities = check_vulnerabilities(file_content)
                results[file_path] = vulnerabilities  # Store results for each Dockerfile
    return results


@app.route("/webhook", methods=["POST"])
def webhook():
    """Webhook to trigger repository scan."""
    payload = request.get_json()
    logging.debug(f"Webhook payload received: {payload}")

    if not payload or "repository" not in payload:
        return jsonify({"error": "Invalid payload: 'repository' key missing"}), 400

    repo_url = payload["repository"]["clone_url"]
    repo_full_name = payload["repository"]["full_name"]
    head_sha = payload.get("after")

    if not head_sha:
        return jsonify({"error": "Invalid payload: 'after' key missing"}), 400

    try:
        jwt_token = generate_jwt()
        installation_id = payload.get("installation", {}).get("id")
        if not installation_id:
            return jsonify({"error": "No installation ID found"}), 400

        access_token = get_installation_access_token(jwt_token, installation_id)
        scan_results = clone_and_scan(repo_url, access_token)

        # Post individual check runs for each Dockerfile
        for file_path, issues in scan_results.items():
            # Use the relative path for better readability in the GitHub Checks tab
            relative_file_path = os.path.relpath(file_path, start=os.getcwd())
            post_check_run(repo_full_name, head_sha, f"Dockerfile Scan - {relative_file_path}", file_path, issues, access_token)

        return jsonify({"status": "completed", "results": scan_results}), 200

    except Exception as e:
        logging.error(f"Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    logging.info("Starting Flask application.")
    app.run(host="0.0.0.0", port=5000)
