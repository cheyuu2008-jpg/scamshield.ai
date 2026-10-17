"""
ScamShield AI - Git & GitHub Automation Utility
Locates git automatically, initializes the local repository, commits all code,
and pushes to a remote GitHub repository.
"""

import os
import sys
import subprocess

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

GIT_PATH = r"C:\Users\kumary shreya\AppData\Local\Microsoft\WinGet\Packages\Git.MinGit_Microsoft.Winget.Source_8wekyb3d8bbwe\cmd\git.exe"
REPO_DIR = os.path.dirname(os.path.abspath(__file__))

def run_git(args, check=True):
    cmd = [GIT_PATH] + args
    print(f"[*] Running: git {' '.join(args)}")
    result = subprocess.run(cmd, cwd=REPO_DIR, text=True, capture_output=True, encoding='utf-8', errors='replace')
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip() and result.returncode != 0:
        print(f"[!] {result.stderr.strip()}")
    if check and result.returncode != 0:
        raise RuntimeError(f"Git command failed: {' '.join(args)}")
    return result

def init_and_commit():
    print("==========================================================")
    print("[+] ScamShield AI - Git Repository Setup")
    print("==========================================================")
    
    # 1. Init if needed
    git_dir = os.path.join(REPO_DIR, ".git")
    if not os.path.exists(git_dir):
        print("[+] Initializing new Git repository on branch 'main'...")
        run_git(["init", "-b", "main"])
    else:
        print("[+] Git repository already initialized.")

    # 2. Config user
    name_check = run_git(["config", "user.name"], check=False)
    if not name_check.stdout.strip():
        run_git(["config", "user.name", "ScamShield Developer"])
        run_git(["config", "user.email", "dev@scamshield.ai"])

    # 3. Add all files
    print("[+] Staging project files...")
    run_git(["add", "."])

    # 4. Commit
    status = run_git(["status", "--porcelain"], check=False).stdout.strip()
    if status:
        print("[+] Creating initial commit...")
        run_git(["commit", "-m", "Initial commit: ScamShield AI Hackathon Prototype (Multi-Vector Fraud Interceptor)"])
        print("[OK] Local commit created successfully!")
    else:
        print("[OK] All files already committed, working tree clean.")

    # 5. Check remote
    remotes = run_git(["remote", "-v"], check=False).stdout.strip()
    print("\n[+] Current Remotes:\n" + (remotes if remotes else "No remote origin configured yet."))

def push_to_remote(remote_url):
    print(f"\n[+] Configuring remote origin: {remote_url}")
    # Check if origin exists
    remotes = run_git(["remote"], check=False).stdout.strip()
    if "origin" in remotes.split():
        run_git(["remote", "set-url", "origin", remote_url])
    else:
        run_git(["remote", "add", "origin", remote_url])

    print("[+] Pushing to GitHub (branch: main)...")
    res = run_git(["push", "-u", "origin", "main"], check=False)
    if res.returncode == 0:
        print("\n[SUCCESS] Project has been pushed to GitHub!")
        print(f"Repository URL: {remote_url}")
    else:
        print("\n[!] Push notice:")
        print(res.stderr.strip() or res.stdout.strip())
        print("\nTip: Make sure the repository exists on GitHub, and your credentials or Personal Access Token (PAT) are configured.")

if __name__ == "__main__":
    init_and_commit()
    
    if len(sys.argv) > 1 and sys.argv[1].startswith("http"):
        push_to_remote(sys.argv[1])
    elif len(sys.argv) > 1 and sys.argv[1] == "--push":
        if len(sys.argv) > 2:
            push_to_remote(sys.argv[2])
        else:
            url = input("\nEnter your GitHub repository URL (e.g., https://github.com/username/scamshield-ai.git): ").strip()
            if url:
                push_to_remote(url)
    else:
        print("\n----------------------------------------------------------")
        print("To push to your GitHub repo, run:")
        print("  python git_sync.py --push https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git")
        print("----------------------------------------------------------")
