"""
ScamShield AI - Git & GitHub Automation Utility
Locates Git and GitHub CLI automatically, initializes the local repository, commits all code,
and pushes to a remote GitHub repository.
"""

import os
import sys
import subprocess

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

GIT_PATH = r"C:\Users\kumary shreya\AppData\Local\Microsoft\WinGet\Packages\Git.MinGit_Microsoft.Winget.Source_8wekyb3d8bbwe\cmd\git.exe"
GH_PATH = r"C:\Users\kumary shreya\AppData\Local\Microsoft\WinGet\Packages\GitHub.cli_Microsoft.Winget.Source_8wekyb3d8bbwe\bin\gh.exe"
REPO_DIR = os.path.dirname(os.path.abspath(__file__))

def run_cmd(cmd_list, check=True):
    print(f"[*] Running: {' '.join(cmd_list)}")
    result = subprocess.run(cmd_list, cwd=REPO_DIR, text=True, capture_output=True, encoding='utf-8', errors='replace')
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip() and result.returncode != 0:
        print(f"[!] {result.stderr.strip()}")
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd_list)}")
    return result

def push_with_gh():
    print("==========================================================")
    print("[+] ScamShield AI - GitHub Automated Push with GitHub CLI")
    print("==========================================================")
    
    # Check auth
    res = run_cmd([GH_PATH, "auth", "status"], check=False)
    if res.returncode != 0:
        print("\n[!] Not logged into GitHub yet.")
        print("[!] Please run 'push_to_github.bat' or 'gh auth login' to sign in via your browser.")
        return False
    
    print("\n[+] Creating repository 'scamshield-ai' and pushing...")
    res = run_cmd([GH_PATH, "repo", "create", "scamshield-ai", "--public", f"--source={REPO_DIR}", "--remote=origin", "--push"], check=False)
    if res.returncode == 0:
        print("\n[SUCCESS] Project successfully created and pushed to GitHub!")
        return True
    else:
        print("\n[!] Repo create encountered an issue, trying direct push...")
        push_res = run_cmd([GIT_PATH, "push", "-u", "origin", "main"], check=False)
        return push_res.returncode == 0

def push_with_url(remote_url):
    print(f"\n[+] Configuring remote origin: {remote_url}")
    remotes = run_cmd([GIT_PATH, "remote"], check=False).stdout.strip()
    if "origin" in remotes.split():
        run_cmd([GIT_PATH, "remote", "set-url", "origin", remote_url])
    else:
        run_cmd([GIT_PATH, "remote", "add", "origin", remote_url])

    print("[+] Pushing to GitHub (branch: main)...")
    res = run_cmd([GIT_PATH, "push", "-u", "origin", "main"], check=False)
    if res.returncode == 0:
        print("\n[SUCCESS] Project has been pushed to GitHub!")
        print(f"Repository URL: {remote_url}")
        return True
    else:
        print("\n[!] Push notice:")
        print(res.stderr.strip() or res.stdout.strip())
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].startswith("http"):
        push_with_url(sys.argv[1])
    elif len(sys.argv) > 1 and sys.argv[1] == "--push":
        if len(sys.argv) > 2:
            push_with_url(sys.argv[2])
        else:
            url = input("\nEnter your GitHub repository URL: ").strip()
            if url:
                push_with_url(url)
    else:
        # Default try gh
        if not push_with_gh():
            print("\nTip: You can push directly with:")
            print("  python git_sync.py --push https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git")
            print("Or double-click push_to_github.bat")
