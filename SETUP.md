# Setting Up Your GitHub Repository

This local repository is ready to push to GitHub. Here's how:

---

## Step 1: Create Empty GitHub Repository

1. Go to https://github.com/new
2. **Repository name**: `ai-personality-book` (or your preferred name)
3. **Description**: "Companion repository for Introduction to AI Personality Development (Oct 2025)"
4. **Visibility**: Public
5. ⚠️ **Do NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

---

## Step 2: Push This Local Repository

GitHub will show you commands. Use these instead:

```bash
# If you're in the ai-personality-book directory already:
git add .
git commit -m "Initial repository setup for AI Personality Development book"

# Replace YOUR-USERNAME with your actual GitHub username:
git remote add origin https://github.com/YOUR-USERNAME/ai-personality-book.git

# Push to GitHub:
git branch -M main
git push -u origin main
```

---

## Step 3: Verify Upload

1. Visit your repository: `https://github.com/YOUR-USERNAME/ai-personality-book`
2. You should see:
   - README.md displaying properly
   - `/errata`, `/updates`, `/resources` directories
   - VERSION file
   - CONTRIBUTING.md

---

## Step 4: Update Book Front Matter

Now you can add this to your book:

```
⚠ UPDATES AVAILABLE ⚠
For errata, corrections, and field updates:
github.com/YOUR-USERNAME/ai-personality-book

Kindle version updates: This book will be revised quarterly.
Check your Kindle library for updates.
```

---

## Step 5: Enable GitHub Pages (Optional)

Want a cleaner URL like `yourusername.github.io/ai-personality-book`?

1. Go to repository Settings → Pages
2. Source: Deploy from branch `main`
3. Folder: `/ (root)`
4. Save
5. Wait ~5 minutes, then visit the URL shown

---

## Step 6: Configure Repository Settings

### Issues & Discussions
- Settings → General → Features
- ✅ Enable Issues
- ✅ Enable Discussions

### Labels for Issues
Consider adding custom labels:
- `errata:critical`
- `errata:moderate`
- `errata:minor`
- `field-update`
- `section-6-methods` (and other sections)

---

## Ongoing Maintenance

### Monthly (10 min):
```bash
# Check for major AI developments
# Update /updates/ files as needed

git add updates/
git commit -m "Monthly update: [brief summary]"
git push
```

### Quarterly (2-3 hours):
```bash
# Review Section 6 against current literature
# Push Kindle update if needed
# Increment VERSION file

git add VERSION
git commit -m "Quarterly review: v1.1 updates"
git push
git tag v1.1
git push --tags
```

---

## Troubleshooting

**Problem**: "remote origin already exists"  
**Solution**: `git remote remove origin` then try again

**Problem**: Permission denied  
**Solution**: Set up SSH keys or use personal access token

**Problem**: "Updates were rejected"  
**Solution**: `git pull origin main --rebase` then `git push`

---

## Need Help?

- GitHub Docs: https://docs.github.com/en/get-started
- Git Basics: https://git-scm.com/book/en/v2/Getting-Started-Git-Basics

---

**You're all set! Your repository is ready to support your book readers.**
