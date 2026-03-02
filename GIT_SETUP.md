# Git & GitHub Setup

Your local git repository is ready! Follow these steps to push to GitHub.

## Step 1: Create a GitHub Repository

1. Go to https://github.com/new
2. Fill in:
   - **Repository name:** `quote-automation`
   - **Description:** `Automated quote generation system with Airtable, Gemini AI, and Gmail`
   - **Visibility:** Public (or Private if you prefer)
   - **Skip** initializing with README/license (we already have them)
3. Click **"Create repository"**

## Step 2: Push Your Code

After creating the repo on GitHub, you'll see instructions. Run these commands:

```bash
cd /Users/roykeren/אוטמציות\ מורכבות\ למערכת/אוטמציית\ הצעת\ מחיר/quote_automation

git remote add origin https://github.com/YOUR_USERNAME/quote-automation.git
git branch -M main
git push -u origin main
```

**Replace `YOUR_USERNAME` with your actual GitHub username!**

## Step 3: Verify

- Go to your GitHub repo
- You should see all your files there
- Note the URL: `https://github.com/YOUR_USERNAME/quote-automation`

## Step 4: For Railway Deployment

When deploying to Railway:
1. Connect your GitHub account
2. Select this repository
3. Railway will auto-deploy on every push to `main`

---

## Current Git Status

```
Repository: quote-automation
Branch: main
Commits: 1 (Initial commit)
Files: 20
Status: Ready to push
```

## Useful Git Commands

```bash
# Check status
git status

# View recent commits
git log --oneline

# Make changes and commit
git add .
git commit -m "Your message"
git push

# Create a new branch
git checkout -b feature/your-feature
git push -u origin feature/your-feature
```

---

**Ready to push? Just run the commands from Step 2!** 🚀
