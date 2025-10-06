# Gmail Automation Setup Guide

## Overview

This guide walks you through configuring Gmail API access for the Job Search Automation Platform. Once configured, the system will automatically scan your inbox, classify job-related emails, and track interview opportunities.

**Time to Complete**: 15-20 minutes
**Prerequisites**: Google account, Gmail access

---

## Step 1: Create Google Cloud Project

### 1.1 Access Google Cloud Console
1. Go to: https://console.cloud.google.com/
2. Sign in with your Google account

### 1.2 Create New Project
1. Click the project dropdown at the top
2. Click **"NEW PROJECT"**
3. **Project name**: `Job-Search-Automation` (or your preference)
4. **Organization**: Leave as "No organization"
5. Click **"CREATE"**
6. Wait ~30 seconds for project creation

### 1.3 Enable Gmail API
1. Ensure your new project is selected in the dropdown
2. Go to: https://console.cloud.google.com/apis/library
3. Search for **"Gmail API"**
4. Click on **"Gmail API"** (first result)
5. Click **"ENABLE"**
6. Wait ~10 seconds for activation

✅ **Checkpoint**: You should see "API enabled" with a green checkmark

---

## Step 2: Create OAuth 2.0 Credentials

### 2.1 Navigate to Credentials
1. In Google Cloud Console, go to: **APIs & Services > Credentials**
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Select **"OAuth client ID"**

### 2.2 Configure OAuth Consent Screen (if prompted)
1. If you see "OAuth consent screen required", click **"CONFIGURE CONSENT SCREEN"**
2. Select **"External"** user type
3. Click **"CREATE"**
4. Fill in required fields:
   - **App name**: `Job Search Automation`
   - **User support email**: Your email
   - **Developer contact email**: Your email
5. Click **"SAVE AND CONTINUE"** through remaining screens
6. Return to Credentials page

### 2.3 Create OAuth Client ID
1. Click **"+ CREATE CREDENTIALS"** again
2. Select **"OAuth client ID"**
3. **Application type**: Select **"Desktop app"**
4. **Name**: `Gmail Desktop Client`
5. Click **"CREATE"**

### 2.4 Handle 2-Secret Limit (if needed)
If you see "You can only create 2 secrets":
1. Click on an existing secret
2. Click **"Disable"** next to the old secret
3. Click the **trash icon (🗑️)** to delete it
4. Return and click **"+ Add secret"**

### 2.5 Download Credentials File
1. A dialog will appear with your client ID and secret
2. Click **"DOWNLOAD JSON"** (this is your ONLY chance!)
3. File will download as: `client_secret_*.json`
4. **IMPORTANT**: Save this file immediately

✅ **Checkpoint**: You have a `client_secret_*.json` file downloaded

---

## Step 3: Install Credentials File

### 3.1 Move to Job_Search Directory
```bash
cd /Users/matthewscott/Desktop/Job_Search

# Move the downloaded file here
mv ~/Downloads/client_secret_*.json ./

# Verify it's in place
ls client_secret_*.json
```

Expected output: `client_secret_234263158377-qne0ms5qlreqnn0k7pm2lg8tl10kev82.apps.googleusercontent.com.json`

### 3.2 Update .env File
The credentials file path should already be in your `.env`. Verify:

```bash
# Check current setting
grep GMAIL_CREDENTIALS_FILE .env
```

Should show the full path to your `client_secret_*.json` file.

✅ **Checkpoint**: Credentials file is in Job_Search directory

---

## Step 4: Run OAuth Flow

### 4.1 Execute Setup Script
```bash
/usr/bin/python3 setup_gmail_simple.py
```

### 4.2 Complete Browser Authentication
1. A browser window will open automatically
2. You may see **"Google hasn't verified this app"** warning:
   - Click **"Advanced"**
   - Click **"Go to Job Search Automation (unsafe)"** (it's safe—it's your app!)
3. Sign in to your Google account (if not already signed in)
4. Review permissions requested:
   - Read emails
   - Modify emails
   - Manage labels
5. Click **"Allow"**

### 4.3 Verify Success
You should see:
```
======================================================================
🎉 SUCCESS! Gmail automation is now configured!
======================================================================

📧 Connected to: your-email@gmail.com
📊 Total messages: XXXXX
📁 Threads total: XXXXX

✅ Token saved to: gmail_token.json
```

✅ **Checkpoint**: `gmail_token.json` file created in Job_Search directory

---

## Step 5: Start the Server

### 5.1 Critical: Unset Environment Variables

**IMPORTANT**: Shell environment variables override `.env` file settings. You MUST unset them:

```bash
unset DATABASE_URL GMAIL_CREDENTIALS_FILE GMAIL_TOKEN_FILE GMAIL_SCOPES
```

### 5.2 Start Uvicorn Server
```bash
/usr/bin/python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8899 --reload
```

### 5.3 Verify Server Started
Look for this output (NO errors about Gmail):
```
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ **Checkpoint**: Server running with no Gmail errors

---

## Step 6: Test Email Scanning

### 6.1 Scan Last 7 Days
```bash
curl -X POST http://localhost:8899/api/v1/email/scan \
  -H "Content-Type: application/json" \
  -d '{"days_back": 7}'
```

### 6.2 Expected Response
```json
{
  "status": "success",
  "emails_processed": XX,
  "results": [
    {
      "subject": "...",
      "from": "...",
      "classification": "INTERVIEW" / "OTHER" / etc,
      "matched_application": null
    }
  ],
  "message": "Email scan completed. Database updated automatically."
}
```

✅ **Checkpoint**: Emails scanned and classified successfully

---

## Troubleshooting

### "Gmail service not initialized" Error

**Cause**: Environment variables blocking `.env` file settings

**Solution**:
```bash
# Check for conflicting env vars
env | grep GMAIL

# If any show up, unset them:
unset DATABASE_URL GMAIL_CREDENTIALS_FILE GMAIL_TOKEN_FILE GMAIL_SCOPES

# Restart server
/usr/bin/python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8899 --reload
```

### "Gmail credentials file not found"

**Cause**: Incorrect path in `.env` or file not moved

**Solution**:
```bash
# Verify file exists
ls client_secret_*.json

# Check .env path
grep GMAIL_CREDENTIALS_FILE .env

# Update .env if needed (use FULL PATH):
GMAIL_CREDENTIALS_FILE=/Users/matthewscott/Desktop/Job_Search/client_secret_2_234263158377-qne0ms5qlreqnn0k7pm2lg8tl10kev82.apps.googleusercontent.com.json
```

### "Token expired" or "Invalid grant"

**Cause**: OAuth token expired or revoked

**Solution**:
```bash
# Delete old token
rm gmail_token.json

# Re-run OAuth flow
/usr/bin/python3 setup_gmail_simple.py
```

### ".env file not loading"

**Cause**: Syntax error in `.env`

**Solution**:
```bash
# Check for common issues:
# 1. Missing newlines between variables
# 2. Spaces around = sign (should be KEY=value, not KEY = value)
# 3. Comments on same line as value without newline

# Test loading:
/usr/bin/python3 test_settings.py
```

---

## Email Classification Keywords

The system uses keyword matching to classify emails:

### Interview Detection
- "interview", "schedule", "availability"
- "zoom", "teams", "phone screen"
- "next steps", "speak with you"
- "calendar", "meet with"

### Rejection Detection
- "unfortunately", "not selected"
- "other candidates", "not moving forward"
- "position has been filled"
- "thank you for your interest"

### Offer Detection
- "offer", "compensation", "salary"
- "benefits", "start date"
- "pleased to offer", "congratulations"

### Info Request Detection
- "additional information", "please provide"
- "could you send", "need more details"
- "clarification", "confirm", "verify"

---

## Automated Scanning Setup (Optional)

### Cron Job (Every 30 Minutes)
```bash
# Edit crontab
crontab -e

# Add this line:
*/30 * * * * cd /Users/matthewscott/Desktop/Job_Search && /usr/bin/python3 -c "import requests; requests.post('http://localhost:8899/api/v1/email/scan', json={'days_back': 7})"
```

### Systemd Service (Linux)
Create `/etc/systemd/system/job-search-email.service`:
```ini
[Unit]
Description=Job Search Email Scanner
After=network.target

[Service]
Type=oneshot
User=matthewscott
WorkingDirectory=/Users/matthewscott/Desktop/Job_Search
ExecStart=/usr/bin/python3 -c "import requests; requests.post('http://localhost:8899/api/v1/email/scan', json={'days_back': 7})"

[Install]
WantedBy=multi-user.target
```

Then create timer:
```bash
sudo systemctl enable job-search-email.timer
sudo systemctl start job-search-email.timer
```

---

## Security Best Practices

### 1. Protect Credentials Files
```bash
# Restrict file permissions
chmod 600 client_secret_*.json
chmod 600 gmail_token.json

# Never commit to git
echo "client_secret_*.json" >> .gitignore
echo "gmail_token.json" >> .gitignore
```

### 2. Token Rotation
- Tokens expire after 7 days of inactivity
- Refresh tokens automatically renew access
- If token becomes invalid, re-run `setup_gmail_simple.py`

### 3. Revoke Access (if needed)
1. Go to: https://myaccount.google.com/permissions
2. Find "Job Search Automation"
3. Click **"Remove access"**
4. Re-run setup if you want to grant access again

---

## Success Metrics

After setup, you should see:
- ✅ Server starts without Gmail errors
- ✅ Email scans complete in <10 seconds
- ✅ Job-related emails classified correctly
- ✅ Interview opportunities detected (if any exist)
- ✅ Emails linked to applications (once applications created)

**Time Saved**: 10+ minutes/day (60.8 hours/year)
**Economic Value**: $2,188/year (at $36/hour Louisville IT salary)

---

## Next Steps

1. **Create applications** for your tracked jobs → Enable email-to-job matching
2. **Set up scheduled scans** → Automate continuous monitoring
3. **View analytics** → `GET /api/v1/email/stats`
4. **Monitor dashboard** → `GET /api/v1/analytics/dashboard`

---

## Support

- **Documentation**: See `CLAUDE.md` for full system overview
- **API Docs**: http://localhost:8899/docs
- **Troubleshooting**: See section above or `CLAUDE.md` troubleshooting section

---

*Last Updated: October 6, 2025*
*Version: 2.2.0*
