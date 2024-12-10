Dockerfile Vulnerability Scanner GitHub App

This GitHub App scans Dockerfiles in your repositories for potential vulnerabilities based on OWASP Top 10 guidelines and other best practices. It reports the findings directly in the repository’s “Checks” tab.

Features
	•	Scans all Dockerfiles within a repository or specific subfolders (e.g., apps/).
	•	Identifies vulnerabilities and provides suggestions to mitigate them.
	•	Categorizes findings according to OWASP Top 10 standards.
	•	Posts individual reports for each Dockerfile in the GitHub “Checks” tab.

Prerequisites
	1.	Python 3.8+
	•	Ensure you have Python installed on your machine. Use pyenv or any package manager to install it.
	2.	Flask
	•	Install Flask using pip:

pip install flask


	3.	PyJWT
	•	Install PyJWT:

pip install pyjwt


	4.	GitPython
	•	Install GitPython:

pip install gitpython


	5.	Requests
	•	Install Requests:

pip install requests


	6.	Smee Client
	•	Install the Smee.io client for forwarding webhooks:

npm install --global smee-client

Setting Up the GitHub App

Step 1: Create a GitHub App
	1.	Go to your GitHub account’s Settings > Developer settings > GitHub Apps.
	2.	Click New GitHub App.
	3.	Fill out the details:
	•	App name: DockerfileVulnerabilityScanner
	•	Homepage URL: URL of your app (if running locally, you can use http://localhost:5000).
	•	Webhook URL: Use a Smee proxy URL for local development (details in the Using Smee.io for Local Development section).
	•	Webhook secret: Add a random secret (this will be used to verify webhook payloads).
	4.	Permissions:
	•	Repository:
	•	Contents: Read-only
	•	Checks: Read & Write
	•	Metadata: Read-only
	5.	Subscribe to events:
	•	push
	6.	Click Create GitHub App.

Step 2: Generate and Download the Private Key
	1.	After creating the app, navigate to the app’s settings.
	2.	Click Generate a private key.
	3.	Download the .pem file and save it securely (e.g., private-key.pem).

Step 3: Install the App
	1.	Go to the app’s settings page.
	2.	Under the Install App section, click Install App.
	3.	Choose the repositories where you want the app to scan Dockerfiles.

Using Smee.io for Local Development

GitHub cannot directly communicate with your local server due to network restrictions. Smee.io acts as a proxy to forward GitHub webhook events to your local machine.

Step 1: Set Up a Proxy URL
	1.	Go to Smee.io and click Start a new channel.
	2.	Copy the generated Webhook Proxy URL (e.g., https://smee.io/YOUR_CHANNEL_ID).

Step 2: Update the GitHub App Webhook URL
	1.	In your GitHub App settings, update the Webhook URL to the Smee Proxy URL you just copied.

Step 3: Run the Smee Client
	1.	Use the following command to forward webhook events to your local server:

smee -u https://smee.io/YOUR_CHANNEL_ID -t http://localhost:5000/webhook

	•	-u: Smee Proxy URL
	•	-t: Your local webhook endpoint (in this case, the Flask app).

	2.	You should see logs in the terminal indicating that webhook requests are being forwarded to your app.

Why Use Smee.io?
	•	Quick Setup: No need to expose your local server publicly or configure firewalls.
	•	Debugging: Logs webhook payloads for easier debugging.
	•	Free & Secure: Provides a secure channel for testing GitHub webhooks.

Running the GitHub App Locally
	1.	Clone the repository:

git clone <your-repo-url>
cd <your-repo-directory>


	2.	Place the .pem file in the repository root:

mv /path/to/private-key.pem ./private-key.pem


	3.	Install the required Python libraries:

pip install -r requirements.txt


	4.	Start the app:

python app.py


	5.	Ensure Smee.io is running to forward webhook events to your local server.

Example Workflow

Step 1: Trigger a Push Event

The app is triggered when you push changes to a repository with Dockerfiles. Each Dockerfile under subfolders like apps/ will have its own report.

Step 2: The App Scans Dockerfiles
	•	The app clones the repository.
	•	It scans every Dockerfile in the folder structure (e.g., apps/).
	•	Vulnerabilities are identified and logged.

Step 3: Results are Posted to the “Checks” Tab
	•	The app posts findings for each Dockerfile individually to the GitHub “Checks” tab of the repository.

Example Folder Structure

Here’s an example folder structure for your repository:

.
├── apps/
│   ├── app1/
│   │   └── Dockerfile
│   ├── app2/
│   │   └── Dockerfile
│   └── app3/
│       └── Dockerfile
└── README.md

Each Dockerfile in apps/ will have its own report in the “Checks” tab.

Troubleshooting

Common Issues
	1.	Webhook Not Working:
	•	Ensure your Smee client is running.
	•	Verify the Smee Proxy URL matches the Webhook URL in the GitHub App settings.
	2.	Missing Results:
	•	Check the logs for issues with file permissions or repository access.
	3.	Authentication Errors:
	•	Ensure the private key (private-key.pem) matches the key associated with your GitHub App.
