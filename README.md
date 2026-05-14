# MLB HR cheat sheet (static site)

This folder is the **live site**: `index.html` is the full cheat sheet. Your builder copies the latest sheet here as `index.html` so the URL never changes—only the file updates.

## One-time: GitHub Pages

1. Install **Git for Windows**: https://git-scm.com/download/win  
   Restart the terminal after install.

2. Create a **new empty repository** on GitHub (no README, no .gitignore):  
   https://github.com/new  
   Suggested name: `mlb-hr-cheatsheet` (must be **Public** for free Pages on a normal account).

3. In PowerShell, from **this folder**:

   ```powershell
   cd $HOME\mlb-hr-cheatsheet-web
   .\setup-github-pages.ps1 -GitHubUser YOUR_GITHUB_USERNAME -RepoName mlb-hr-cheatsheet
   ```

   If the script says `git` was not found, fix your PATH or open **Git Bash** and run the `git` commands printed at the end of the script manually.

4. On GitHub: **Settings → Pages → Build and deployment**  
   - **Source:** Deploy from a branch  
   - **Branch:** `main` and folder **`/ (root)`**  
   - Save.

5. Your site (after a minute or two):

   `https://YOUR_GITHUB_USERNAME.github.io/mlb-hr-cheatsheet/`

## After each new cheat sheet

Run your usual build (e.g. `python _build_5_14_sheet.py`), then from this folder:

```powershell
cd $HOME\mlb-hr-cheatsheet-web
git add index.html
git commit -m "Update cheat sheet"
git push
```

Or run `python $HOME\_sync_cheatsheet_site.py` first if you build only the dated HTML, then `git add` / `commit` / `push` as above.
