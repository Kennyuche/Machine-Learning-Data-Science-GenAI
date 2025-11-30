# Datacom Kudos (Minimal Implementation)

This is a minimal, spec-driven implementation of a Kudos system (prototype/demo).

Run locally (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python server.py
```

Then open `http://127.0.0.1:5000` in your browser.

Seeded users: `alice`, `bob`, `carol` (carol is admin).

Notes:
- This is a demo app using SQLite and a simple session-based login (select username).
- For production, replace auth with SSO/OAuth, use a resilient DB, and add tests and CI.

To create a git repo and push to GitHub:

```powershell
cd .\
git init
git add .
git commit -m "Initial kudos prototype"
# create a new GitHub repo and push: follow GitHub UI to create an empty repo and then
git remote add origin https://github.com/<your-username>/<repo>.git
git push -u origin main
```
