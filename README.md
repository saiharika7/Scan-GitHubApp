
# Dockerfile Vulnerability Scanner GitHub App

This GitHub App scans all `Dockerfile`s in your repositories for potential vulnerabilities based on OWASP Top 10 guidelines and best practices. Each scan result is reported individually in the repository's "Checks" tab.

---

## Features
- Scans `Dockerfile` in all subfolders (e.g., `apps/app1/Dockerfile`).
- Identifies vulnerabilities and provides actionable suggestions.
- Categorizes findings according to OWASP Top 10 vulnerabilities.
- Posts individual reports for each `Dockerfile` in the "Checks" tab.
- Works seamlessly with **Smee.io** for local testing.

---

## Prerequisites
1. **Python 3.8+**
   - Ensure Python is installed on your machine.
   - Install required libraries using:
     ```bash
     pip install flask jwt gitpython requests
     ```

2. **Node.js** (for **Smee.io**):
   - Install Node.js if you haven't already:
     ```bash
     sudo apt install nodejs npm # Linux
     brew install node           # macOS
     ```

3. **Smee.io Client**:
   - Install Smee.io globally:
     ```bash
     npm install --global smee-client
     ```

---

## Setting Up the GitHub App

### Step 1: Create a GitHub App
1. Go to **Settings** > **Developer settings** > **GitHub Apps** in your GitHub account.
2. Click **New GitHub App** and configure:
   - **App Name**: `DockerfileVulnerabilityScanner`
   - **Homepage URL**: Your app’s homepage (use `http://localhost:5000` for local development).
   - **Webhook URL**: Use the Smee Proxy URL (`https://smee.io/your-channel-id` for local testing).
   - **Webhook Secret**: Add a random secret (used to verify webhook payloads).

3. **Permissions**:
   - **Repository**:
     - `Contents`: **Read-only**
     - `Checks`: **Read & Write**
   - **Metadata**: **Read-only**

4. **Subscribe to Events**:
   - `push`

5. Click **Create GitHub App**.

---

### Step 2: Generate and Download the Private Key
1. After creating the app, go to the app's settings.
2. Click **Generate a private key**.
3. Save the `.pem` file in the root of your project directory as `private-key.pem`.

---

### Step 3: Install the App
1. Go to the app's settings page.
2. Under **Install App**, click **Install**.
3. Select the repositories you want the app to scan.

---

## Using Smee.io for Local Development

1. Go to [Smee.io](https://smee.io/) and click **Start a new channel**.
2. Copy the generated URL (e.g., `https://smee.io/YOUR_CHANNEL_ID`).
3. In your GitHub App settings, update the **Webhook URL** to the Smee Proxy URL.
4. Run the Smee.io client to forward webhooks:
   ```bash
   smee -u https://smee.io/YOUR_CHANNEL_ID --port 5000
   ```

---

## Running the App

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Ensure Smee.io is forwarding webhooks to the app.

---

## Additional Notes

- Ensure the `private-key.pem` file is in the root directory of the app.
- This app scans all `Dockerfile`s in subfolders and posts individual results to the "Checks" tab.

---

## Troubleshooting

- **Missing Permissions**: Ensure the app has `Read & Write` permissions for checks and `Read-only` for repository contents.
- **Webhook Errors**: Verify the webhook secret and the Smee Proxy URL in your GitHub App settings.
