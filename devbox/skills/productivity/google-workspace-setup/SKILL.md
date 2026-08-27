---
name: google-workspace-setup
description: "Guidance and commands for setting up Google Workspace integration."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Google, Workspace, Setup, OAuth, Configuration, Email, Calendar, Drive, Docs, Sheets]
---

# Google Workspace Setup

This skill provides the step-by-step process for setting up the Google Workspace skill, including OAuth authorization and credential management.

## Prerequisites

1.  **Google Cloud Project**: You need a Google Cloud project with the necessary APIs enabled (Gmail, Calendar, Drive, Sheets, Docs, People API).
2.  **OAuth 2.0 Client ID**: Create an "OAuth 2.0 Client ID" of type "Desktop app" within your Google Cloud project. Download the JSON secret file.
3.  **Advanced Protection (Optional)**: If your Google account uses Advanced Protection, your Workspace administrator must allowlist the OAuth client ID.

## Setup Steps

Follow these steps to authorize Hermes Agent to access your Google Workspace data.

### Step 1: Provide Client Secret File

You will need to provide the path to the `client_secret.json` file you downloaded from the Google Cloud Console.

**Action**: Please provide the **absolute path** to your `client_secret.json` file. For example: `~/Downloads/client_secret_....json`

### Step 2: Specify Services

Tell me which Google services you need access to. This determines the required scopes for authorization.

**Action**: Choose the services you need:
- `email`
- `calendar`
- `drive`
- `docs`
- `sheets`
- `contacts`
- `all` (for full access)

Example input: `email,calendar,drive`

### Step 3: Authorization URL Generation

Once I have the client secret path and service list, I will generate an authorization URL. You will need to open this URL in your browser, log in to your Google account, and grant permission.

### Step 4: Redirect URL Handling

After you grant permission, your browser will redirect to a local URL (likely `http://localhost:1`). This redirect will fail, but it will contain an authorization `code` or a full OAuth URL.

**Action**: **Copy the *entire* redirected URL** from your browser's address bar and provide it back to me.

### Step 5: Complete Authorization

I will use the provided URL/code to complete the authorization process and save the necessary credentials.

### Troubleshooting

-   **`ACCESS_DENIED` Error**: If you receive an `access_denied` error during authorization, it most likely means your Google account is not listed as a test user in the Google Cloud Console's OAuth consent screen or that your Workspace admin has not allowed the client ID. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials) to manage test users or have your admin whitelist the client ID.
-   **Expired/Used Code**: If the authorization code expires or has been used, a new authorization URL will be provided. Repeat Step 4 with the new URL.
-   **Insufficient Permission**: If commands fail with insufficient permission errors after setup, it might mean the initial scopes were too narrow. You may need to re-run the setup process (`$GSETUP --revoke` and then restart the flow) with a broader set of services.
-   **Missing Dependencies**: Ensure you have `google-auth` and `google-api-python-client` installed. If not, you can install them using `python -m pip install google-auth google-api-python-client --upgrade`. Or, install the `gws` CLI tool from its GitHub repository and run `$GSETUP --install-deps`.

## Usage

**Environment Variable**: Set `GAPI` as a shorthand for the Google API script:
\`\`\`bash
GAPI="python \${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/google_api.py"
\`\`\`

Refer to the `google-workspace` skill's main documentation for detailed API usage examples.
