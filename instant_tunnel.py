import subprocess
import time
import re
import os

PORTS = {
    "8080": "url8080.txt",
    "5001": "url5001.txt",
    "5002": "url5002.txt",
    "5003": "url5003.txt",
    "22": "url5003.txt",
}

RETRY_DELAY = 5
CF_PATH = "/usr/bin/cloudflared"

# direktori output
OUT_DIR = "/home/user/online/"
os.makedirs(OUT_DIR, exist_ok=True)

def try_start_tunnel(port):
    """Coba sekali, return url kalau dapat, kalau gagal return None."""
    print(f"\n[TRY] Port {port} → start cloudflare tunnel")

    cmd = [CF_PATH, "tunnel", "--url", f"http://localhost:{port}"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    url = None
    start_time = time.time()

    while True:
        line = proc.stdout.readline()
        if not line:
            break

        print(f"  {line.strip()}")
        m = re.search(r"https://[-a-zA-Z0-9\.]+trycloudflare\.com", line)

        if m:
            url = m.group(0)
            break

        # timeout baca output
        if time.time() - start_time > 15:
            break

    # tutup jika URL tidak dapat
    if not url:
        proc.terminate()
        return None, None

    return url, proc


def write_url(filename, url):
    fullpath = os.path.join(OUT_DIR, filename)
    with open(fullpath, "w") as f:
        f.write(url)
    print(f"[SAVE] {fullpath} → {url}")


if __name__ == "__main__":

    processes = {}      # port → process
    results = {}        # port → url or None

    # ==========================================
    # 1) COBA SEMUA PORT SEKALI DULU
    # ==========================================
    print("\n=========== MULAI SCAN SEMUA PORT ===========")

    for port, fname in PORTS.items():
        url, proc = try_start_tunnel(port)
        results[port] = url

        if url:
            processes[port] = proc
            print(f"[OK] Port {port} dapat URL → {url}")
            write_url(fname, url)
        else:
            print(f"[FAIL] Port {port} belum dapat URL")

    # ==========================================
    # 2) LOOP ULANGI HANYA YANG GAGAL
    # ==========================================
    while True:
        failed = [p for p, url in results.items() if url is None]

        if not failed:
            print("\n🎉 Semua port sudah dapat URL! Sistem aktif penuh.\n")
            break

        print(f"\n[RETRY] Port gagal: {failed}. Coba lagi {RETRY_DELAY} detik...")
        time.sleep(RETRY_DELAY)

        for port in failed:
            fname = PORTS[port]
            url, proc = try_start_tunnel(port)

            if url:
                results[port] = url
                processes[port] = proc
                write_url(fname, url)
                print(f"[OK] Port {port} berhasil setelah retry → {url}")
            else:
                print(f"[FAIL] Port {port} masih gagal, lanjut...")

    # ==========================================
    # 3) KEEPRUNNING (standby) sampai CTRL+C
    # ==========================================
    print("All tunnels running. Tekan CTRL+C untuk stop.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMenutup semua tunnel...")
        for p in processes.values():
            p.terminate()
        print("Selesai.")
