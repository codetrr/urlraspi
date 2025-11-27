import os
import time
import subprocess
from datetime import datetime

FOLDER = "/home/user/online"
FILE = "File.txt"
REPO = FOLDER

PATH = os.path.join(FOLDER, FILE)

def get_subdomain():
    try:
        with open(PATH, "r") as f:
            content = f.read().strip()
        # contoh: https://abcd123.trycloudflare.com
        if "trycloudflare.com" in content:
            # ambil bagian XXX
            return content.split("//")[-1].split(".")[0]
        return ""
    except:
        return ""

def git_push():
    print("[GIT] Subdomain berubah → upload GitHub")
    try:
        subprocess.call(["git", "add", "."], cwd=REPO)
        subprocess.call([
            "git", "commit", "-m",
            f"Auto update subdomain {datetime.now()}"
        ], cwd=REPO)
        subprocess.call(["git", "push"], cwd=REPO)
    except Exception as e:
        print("GIT ERROR:", e)

def main():
    last_sub = ""

    print("Monitoring subdomain trycloudflare...")

    while True:
        current_sub = get_subdomain()

        if current_sub and current_sub != last_sub:
            print(f"[CHANGE] {last_sub} → {current_sub}")
            git_push()
            last_sub = current_sub

        time.sleep(3)

if __name__ == "__main__":
    main()
