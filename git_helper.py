import os
import subprocess
import sys

def find_git():
    # Check standard paths
    possible_paths = [
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs"),
        r"C:\Program Files\Git\cmd",
        r"C:\Program Files\Git\bin",
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WindowsApps"),
    ]
    
    # Direct check
    for p in possible_paths:
        if os.path.exists(p):
            for root, dirs, files in os.walk(p):
                if "git.exe" in files:
                    full_path = os.path.join(root, "git.exe")
                    return full_path
    
    # Try where git
    try:
        out = subprocess.check_output(["where", "git"], text=True)
        lines = [line.strip() for line in out.splitlines() if line.strip()]
        if lines:
            return lines[0]
    except Exception:
        pass
    
    return None

if __name__ == "__main__":
    git_bin = find_git()
    print("FOUND_GIT:", git_bin)
    if git_bin:
        res = subprocess.run([git_bin, "--version"], capture_output=True, text=True)
        print("VERSION:", res.stdout.strip())
