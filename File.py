import os
import time
import subprocess
from datetime import datetime

# Folder kerja
FOLDER = "/home/user/online"
REPO = FOLDER

# Daftar file URL
FILES = [
    "url8080.txt",
    "url5001.txt",
    "url5002.txt",
    "url5003.txt"
]

# Ambil bagian subdomain "XXX" dari "https://XXX.trycloudflare.com"
def extract_subdomain(url: str):
    url = url.strip()
    if "trycloudflare.com" in url:
        # contoh "https://abc123.trycloudflare.com"
        return url.split("//")[-1].split(".")[0]
    return ""

# Baca isi file dan ekstrak subdomain
def read_subdomain(filepath: str):
    try:
        with open(filepath, "r") as f:
            content = f.read()
        return extract_subdomain(content)
    except:
        return ""

# Upload ke GitHub
def git_push(changed_file):
    print(f"[GIT] Upload perubahan dari {changed_file} ...")
    try:
        subprocess.call(["git", "add", "."], cwd=REPO)
        subprocess.call([
            "git", "commit", "-m",
            f"Auto update {changed_file} - {datetime.now()}"
        ], cwd=REPO)
        subprocess.call(["git", "push"], cwd=REPO)
    except Exception as e:
        print("GIT ERROR:", e)

def main():
    print("Monitoring 4 URL TryCloudflare...")

    # Simpan subdomain terakhir
    last = {f: "" for f in FILES}

    while True:
        for f in FILES:
            path = os.path.join(FOLDER, f)
            sub = read_subdomain(path)

            if sub and sub != last[f]:
                print(f"[CHANGE] {f}: {last[f]} → {sub}")
                git_push(f)
                last[f] = sub

        time.sleep(3)

if __name__ == "__main__":
    main()
