# Quote Automation System

A Python-based automated quote generation system that:
- Monitors Airtable for leads ready to receive quotes
- Generates personalized paragraphs using Google Gemini AI
- Creates and fills Google Docs with client information
- Exports documents as PDF
- Sends personalized emails with PDF attachments
- Notifies Roy when each quote is sent

## Improvements Over n8n

✅ **Multi-service support** - Fetches all services at once, not just the first one
✅ **Error handling & retry logic** - Exponential backoff, logs everything
✅ **Persistent logging** - Full audit trail in `logs/quote_automation.log`
✅ **Document link storage** - Saves Google Doc URL back to Airtable
✅ **HTML emails** - RTL-aware formatted emails with inline links
✅ **Roy notifications** - Email notification after each successful send
✅ **Modular architecture** - Clean separation of concerns

## Setup

### 1. Install Dependencies

```bash
cd quote_automation
pip install -r requirements.txt
```

### 2. Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable these APIs:
   - Google Docs API
   - Google Drive API
   - Gmail API
4. Create an "OAuth 2.0 Client ID" (Desktop app)
5. Download the JSON credentials and save as `credentials.json` in this directory

### 3. Airtable Preparation

1. Add a new **URL** field to your Leads table called `קישור להצעה` (or customize in `.env`)
2. Make sure your Leads table has these fields:
   - `שם הליד` (Lead Name)
   - `סיכום חכם` (Call Summary)
   - `שירות מבוקש` (Requested Service) - can be multiple
   - `אימייל` (Email)
   - `שלב הבא` (Next Step)

3. Make sure your Services table has:
   - `שם השירות` (Service Name)
   - `מה כלול` (What's Included)
   - `מחיר` (Price)

### 4. Configure Environment

1. Copy `.env.example` to `.env`
   ```bash
   cp .env.example .env
   ```

2. Fill in your actual values:
   ```ini
   # Get from Airtable
   AIRTABLE_API_KEY=pat_xxxxx
   AIRTABLE_BASE_ID=appxxxxx
   AIRTABLE_LEADS_TABLE_ID=tblxxxxx
   AIRTABLE_SERVICES_TABLE_ID=tblxxxxx

   # Google (auto-handled after first run)
   GOOGLE_CREDENTIALS_FILE=credentials.json
   GOOGLE_TOKEN_FILE=token.json
   GOOGLE_DOC_TEMPLATE_ID=1Lxxxxx (your Google Doc template)

   # Get from Google Cloud
   GEMINI_API_KEY=AIzaSyxxxxx

   # Your email addresses
   GMAIL_SENDER=you@gmail.com
   ROY_NOTIFICATION_EMAIL=roy@example.com

   # Leave as-is unless you changed field names in Airtable
   FIELD_LEAD_NAME=שם הליד
   FIELD_SUMMARY=סיכום חכם
   FIELD_SERVICE=שירות מבוקש
   FIELD_EMAIL=אימייל
   FIELD_NEXT_STEP=שלב הבא
   FIELD_DOC_LINK=קישור להצעה
   ```

### 5. Run

```bash
python main.py
```

On first run, a browser window will open for Google authorization. After you approve, the system runs headless from then on.

## Usage

1. In Airtable, set a lead's `שלב הבא` (Next Step) to `לשלוח הצעה` (Send Quote)
2. The system checks every 60 seconds (configurable in `.env`)
3. When found, it:
   - Fetches service details
   - Generates a personalized paragraph with Gemini
   - Copies and fills your Google Doc template
   - Exports as PDF
   - Sends it via email
   - Marks the lead as `הצעה נשלחה` (Quote Sent)
   - Saves the doc link to Airtable
   - Notifies Roy

## Logs

All activity is logged to `logs/quote_automation.log`. Check this file to debug any issues.

## Running Continuously

### macOS (using launchd)

Create `~/Library/LaunchAgents/com.quoteautomation.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.quoteautomation</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/quote_automation/main.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/quote_automation</string>
    <key>StandardOutPath</key>
    <string>/tmp/quote_automation_out.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/quote_automation_err.log</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Then:
```bash
launchctl load ~/Library/LaunchAgents/com.quoteautomation.plist
```

### Linux

Use `nohup`:
```bash
nohup python main.py > quote_automation.log 2>&1 &
```

Or with systemd service file for auto-start on boot.

## Troubleshooting

**"Missing required environment variables"**
- Check that `.env` exists and all variables are set
- Run `cat .env` to verify

**"Credentials file not found"**
- Download `credentials.json` from Google Cloud Console and place it in the project root

**"Gmail API not enabled"**
- Go to Google Cloud Console → APIs → Gmail API → Enable

**No leads being processed**
- Check `logs/quote_automation.log` for errors
- Make sure at least one lead has `שלב הבא` = `לשלוח הצעה`
- Verify Airtable API key and base/table IDs are correct

## Architecture

```
main.py                    # Entry point, polling loop
├── services/
│   ├── airtable_client.py     # Airtable reads/writes
│   ├── gemini_client.py       # AI paragraph generation
│   ├── google_docs_client.py  # Doc creation and filling
│   ├── google_drive_client.py # PDF export
│   └── gmail_client.py        # Email sending
├── models/
│   └── lead.py               # Data classes
└── utils/
    ├── logger.py             # Logging setup
    └── retry.py              # Retry decorator with backoff
```

Each service is independent and can be tested/mocked separately.
