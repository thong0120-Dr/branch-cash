import subprocess
import urllib.request
import json
import os
import time

# 1. Get Token from git credential helper
p = subprocess.Popen(['git', 'credential', 'fill'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
stdout, _ = p.communicate(input='protocol=https\nhost=github.com\n\n')
token = ''
for line in stdout.splitlines():
    if line.startswith('password='):
        token = line.split('=', 1)[1]

if not token:
    raise Exception("Could not find GitHub token")

headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'BranchCashDeployer'
}

repo_name = "branch-cash"

# 2. Create Repository on GitHub
print("Creating repository on GitHub...")
create_data = json.dumps({
    "name": repo_name,
    "description": "BranchCash - ระบบลงค่าใช้จ่ายและแคชโฟลว์รายสาขา",
    "private": False,
    "has_issues": False,
    "has_wiki": False
}).encode('utf-8')

req = urllib.request.Request('https://api.github.com/user/repos', data=create_data, headers=headers, method='POST')
try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        print(f"Created repo: {res.get('html_url')}")
except urllib.error.HTTPError as e:
    err_body = e.read().decode()
    if "name already exists" in err_body:
        print("Repo already exists, proceeding...")
    else:
        print("Create repo error:", err_body)

# 3. Prepare Local Directory
work_dir = r"C:\Users\COm\.gemini\antigravity\scratch\branch-cashflow"
nojekyll = os.path.join(work_dir, ".nojekyll")
with open(nojekyll, "w") as f:
    f.write("")

readme = os.path.join(work_dir, "README.md")
with open(readme, "w", encoding="utf-8") as f:
    f.write("# BranchCash\nระบบลงค่าใช้จ่ายและแคชโฟลว์ 6 สาขา (เชียงใหม่, ลำพูน, ลำปาง, บางพลี, ระยอง, ส่วนตัว)\n")

# Clean temp js file
tmp_js = os.path.join(work_dir, "get_surge.js")
if os.path.exists(tmp_js):
    os.remove(tmp_js)

# 4. Git Init, Add, Commit, Push
print("Pushing code to GitHub...")
cmds = [
    ["git", "init"],
    ["git", "config", "user.name", "thong0120-Dr"],
    ["git", "config", "user.email", "chayapa.business@gmail.com"],
    ["git", "add", "."],
    ["git", "commit", "-m", "Initial commit: BranchCash web app"],
    ["git", "branch", "-M", "main"],
    ["git", "remote", "remove", "origin"],
    ["git", "remote", "add", "origin", f"https://x-access-token:{token}@github.com/thong0120-Dr/{repo_name}.git"],
    ["git", "push", "-u", "origin", "main", "--force"]
]

for cmd in cmds:
    res = subprocess.run(cmd, cwd=work_dir, capture_output=True, text=True)
    if res.returncode != 0 and "remove" not in cmd[1]:
        print(f"Cmd {' '.join(cmd)}: {res.stderr.strip()}")

print("Pushed successfully!")

# 5. Enable GitHub Pages
print("Enabling GitHub Pages...")
pages_data = json.dumps({
    "source": {
        "branch": "main",
        "path": "/"
    }
}).encode('utf-8')

req_pages = urllib.request.Request(f'https://api.github.com/repos/thong0120-Dr/{repo_name}/pages', data=pages_data, headers=headers, method='POST')
try:
    with urllib.request.urlopen(req_pages) as resp:
        p_res = json.loads(resp.read().decode())
        print("GitHub Pages enabled:", p_res.get('html_url'))
except urllib.error.HTTPError as e:
    err = e.read().decode()
    print("Pages enable response:", err)

# Reset remote without token embedded for safety
subprocess.run(["git", "remote", "set-url", "origin", f"https://github.com/thong0120-Dr/{repo_name}.git"], cwd=work_dir)

print("\n=== DEPLOYMENT COMPLETE ===")
print(f"URL: https://thong0120-dr.github.io/{repo_name}/")
