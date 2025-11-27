import subprocess
import time
import re

# ============================
# Konfigurasi Port
# ============================
PORTS = {
    "8080": "url8080.txt",
    "5001": "url5001.txt",
    "5002": "url5002.txt",
    "5003": "url5003.txt",
}

# ============================
# Fungsi start tunnel
# ============================
def start_tunnel(port):
    print(f"[INFO] Membuat tunnel untuk port {port} ...")

    cmd = [
        "cloudflared", "tunnel", "--url", f"http://localhost:{port}"
    ]

    # jalankan dan ambil output
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    url = None

    # tunggu sampai URL muncul
    while True:
        line = proc.stdout.readline()
        if not line:
            break

        print(line.strip())

        m = re.search(r"https://[-a-zA-Z0-9\.]+trycloudflare\.com", line)
        if m:
            url = m.group(0)
            break

    return url, proc


# ============================
# MAIN
# ============================
procs = []

for port, filename in PORTS.items():
    url, proc = start_tunnel(port)
    procs.append(proc)

    if url:
        with open(filename, "w") as f:
            f.write(url)
        print(f"[OK] URL port {port} disimpan ke {filename} → {url}")
    else:
        print(f"[ERROR] Gagal mendapatkan URL untuk port {port}")

print("\nSemua tunnel sudah dijalankan dan URL disimpan.")
print("Tekan CTRL+C untuk menghentikan semua tunnel.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Menutup semua tunnel...")
    for p in procs:
        p.terminate()
