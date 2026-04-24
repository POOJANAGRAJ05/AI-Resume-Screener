# Git Cleanup & Push Commands

## 1. Remove __pycache__ and .venv from Git Tracking

```bash
# Remove __pycache__ from Git (but keep .gitignore preventing future tracking)
git rm -r --cached __pycache__
git rm -r --cached .venv --ignored

# Remove AI_Resume_Screener/ duplicate folder (if it's redundant)
git rm -r --cached AI_Resume_Screener

# Remove development files from tracking
git rm --cached test_matching.py UI_IMPROVEMENTS.md
```

## 2. Verify Changes

```bash
# See what will be staged/removed
git status

# Preview changes before committing
git diff --cached
```

## 3. Stage Clean Files

```bash
# Stage all changes
git add -A

# Or stage specific important files
git add app.py requirements.txt utils/ README.md .gitignore
```

## 4. Commit with Message

```bash
git commit -m "Cleaned repository for production: removed cache, venv, debug files, and added .gitignore"
```

## 5. Push to GitHub

```bash
# Push main branch
git push -u origin main

# Or if on different branch
git push -u origin <branch-name>
```

## 6. Verify Remote (Optional)

```bash
# Check what's on remote
git ls-remote origin

# View commit history
git log --oneline -10
```

---

### File Cleanup Checklist

- ✅ `.gitignore` - Created with proper exclusions
- ✅ `README.md` - Professional readme with full documentation  
- ✅ `app.py` - Main application (cleaned, no debug prints)
- ✅ `requirements.txt` - Dependencies list
- ✅ `utils/` - Core utility modules (parser.py, skills.py, similarity.py)
- ❌ `test_matching.py` - Remove from tracking (development only)
- ❌ `UI_IMPROVEMENTS.md` - Remove from tracking (internal notes)
- ❌ `AI_Resume_Screener/` - Remove duplicate folder from tracking
- ❌ `__pycache__/` - Will be ignored by .gitignore
- ❌ `.venv/` - Will be ignored by .gitignore

---

### Quick Cleanup Script (All-in-One)

```bash
# Run these commands in sequence
git rm -r --cached __pycache__ 2>/dev/null || true
git rm -r --cached .venv 2>/dev/null || true
git rm -r --cached AI_Resume_Screener 2>/dev/null || true
git rm --cached test_matching.py UI_IMPROVEMENTS.md 2>/dev/null || true
git add -A
git commit -m "Cleaned repository for production: removed cache, venv, debug files, and added .gitignore"
git push -u origin main
```

---

### Final Verification

After pushing, verify:
```bash
# Check remote files
git ls-files | grep -E "(pycache|venv|test_matching|UI_IMPROVEMENTS|AI_Resume_Screener/)"

# Should return nothing - confirming clean repository
```
