# Deploying to Railway

Your Quote Automation system is ready to deploy to Railway! ✅

## Prerequisites

- Railway account (free tier works): https://railway.app
- Git installed on your computer
- Your `credentials.json` and `.env` file (already in place)

## Deployment Steps

### 1. Create a Git Repository

```bash
cd quote_automation
git init
git add .
git commit -m "Initial commit: Quote automation system"
```

### 2. Create Railway Project

- Go to https://railway.app
- Click **"New Project"**
- Select **"Deploy from GitHub"** (or create new repo)
- Authorize GitHub if needed

### 3. Connect Your Repository

- Push to GitHub:
  ```bash
  git remote add origin https://github.com/YOUR_USERNAME/quote-automation.git
  git branch -M main
  git push -u origin main
  ```

- In Railway, connect to your GitHub repo

### 4. Configure Environment Variables

In Railway project settings:

- Go to **Variables**
- Add all variables from your `.env` file:
  ```
  AIRTABLE_API_KEY=patipb3SAbKt...
  AIRTABLE_BASE_ID=appgllvpetmbT3Q4J
  AIRTABLE_LEADS_TABLE_ID=tblSOEpbpsluZ82Je
  AIRTABLE_SERVICES_TABLE_ID=tblV3CdQQH41nqAeh
  GEMINI_API_KEY=AIzaSyD8SexOM...
  GEMINI_MODEL=gemini-2.5-flash
  GOOGLE_DOC_TEMPLATE_ID=1LGlWNGdDxebpKjKG5NlvhxLiuFYw6clUB79V1bWNnlY
  GMAIL_SENDER=roy@example.com
  ROY_NOTIFICATION_EMAIL=roy@example.com
  GOOGLE_CREDENTIALS_FILE=credentials.json
  GOOGLE_TOKEN_FILE=token.json
  POLL_INTERVAL_SECONDS=60
  ```

### 5. Upload credentials.json

Since `credentials.json` is in `.gitignore` (secure!), you need to:

**Option A: Remove from .gitignore temporarily**
```bash
# Edit .gitignore - remove or comment out the credentials.json line
git add credentials.json
git commit -m "Add Google credentials"
git push
```
Then add it back to `.gitignore` for safety.

**Option B: Use Railway's file upload**
- In Railway, go to **Files**
- Upload `credentials.json`
- Update `GOOGLE_CREDENTIALS_FILE=/home/railway/credentials.json`

### 6. Deploy

- Push your code to main branch
- Railway auto-deploys
- Check the deployment logs to verify it's running

### 7. Monitor

- Go to Railway **Deployments**
- View logs to see automation running
- Every 60 seconds it polls Airtable for new leads

## What Happens

Once deployed to Railway:

1. ✅ Automation runs 24/7
2. ✅ Polls Airtable every 60 seconds
3. ✅ On new quote requests: generates PDF → sends email → updates Airtable
4. ✅ Logs all activity (viewable in Railway)
5. ✅ Automatic restarts if crashes

## Troubleshooting

**"ModuleNotFoundError"**
- Check Railway's Python version (should be 3.11-3.13)
- Verify `requirements.txt` is in root of project

**"Missing environment variables"**
- Double-check all vars are added in Railway dashboard
- Restart the deployment

**"Google authentication failed"**
- Verify `credentials.json` path is correct
- First deployment: app opens browser (won't work on server)
  - Solution: Generate `token.json` locally, then upload to Railway

## Pricing

Railway's free tier includes:
- $5/month free credits
- Up to 500 hours of runtime
- Perfect for this automation!

## Support

Need help? Check Railway docs: https://docs.railway.app

---

**Your automation is production-ready!** 🚀
