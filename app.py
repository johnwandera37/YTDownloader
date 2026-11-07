import os
import re
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

def get_app_dir():
    # Use the bin next to the .exe file (Useful for portability) default to the path in %LOCALAPPDATA%
    base = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
    if (base / "bin").exists():
        return base
    return Path(os.environ.get("LOCALAPPDATA", Path.home())) / "YTDownloader"

APP_DIR = get_app_dir()
BIN_DIR = APP_DIR / "bin"
DEFAULT_OUT = Path.home() / "Downloads" / "YTDownloader"

TOOLS = {
    "yt-dlp": ("https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe", None),
    "ffmpeg": ("https://github.com/yt-dlp/FFmpeg-Builds/releases/latest/download/ffmpeg-master-latest-win64-gpl.zip", ["ffmpeg.exe", "ffprobe.exe"]),
    "deno": ("https://github.com/denoland/deno/releases/latest/download/deno-x86_64-pc-windows-msvc.zip", ["deno.exe"]),
}


def progress(block, block_size, total):
    if total > 0:
        pct = min(100, block * block_size * 100 // total)
        print(f"\r  {pct}%", end="", flush=True)


# If the connection drops halfway, a broken exe is left behind, and ensure_tools() sees the file and thinks the tool is installed. It will stay broken until someone deletes it by hand
# The fix is to download to a .part file and rename on success, which is a three-line change to download()
def download(url, dest):
    dest = Path(dest)
    part = dest.with_name(dest.name + ".part")
    urllib.request.urlretrieve(url, part, progress)
    os.replace(part, dest)
    print()


def install_tool(name):
    url, exes = TOOLS[name]
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {name}...")
    if exes is None:  # single exe
        download(url, BIN_DIR / f"{name}.exe")
        return
    zip_path = APP_DIR / f"{name}.zip"
    download(url, zip_path)
    with zipfile.ZipFile(zip_path) as z:
        for member in z.namelist():
            if os.path.basename(member) in exes:
                with z.open(member) as src, open(BIN_DIR / os.path.basename(member), "wb") as dst:
                    dst.write(src.read())
    zip_path.unlink()


def ensure_tools():
    missing = [n for n, (_, exes) in TOOLS.items()
               if not (BIN_DIR / ((exes or [f"{n}.exe"])[0])).exists()]
    if missing:
        print("First run: setting up required tools (one time only)...\n")
        for name in missing:
            install_tool(name)
        print("Setup complete.\n")


def ask(prompt, options, default=1):
    """Numbered menu. Enter = default."""
    print(f"\n{prompt}")
    for i, label in enumerate(options, 1):
        print(f"  {i}. {label}" + ("  (default)" if i == default else ""))
    while True:
        raw = input("> ").strip()
        if raw == "":
            return default
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return int(raw)
        print("Please enter one of the numbers above.")


def run_ytdlp(args):
    env = os.environ.copy()
    env["PATH"] = str(BIN_DIR) + os.pathsep + env["PATH"]  # so yt-dlp finds deno
    cmd = [str(BIN_DIR / "yt-dlp.exe"), "--ffmpeg-location", str(BIN_DIR)] + args
    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\nCancelled.")


def download_flow():
    url = input("\nPaste the YouTube link: ").strip()
    if not url:
        return

    args = []
    is_playlist_url = "list=" in url
    playlist = False

    if is_playlist_url:
        is_mix = bool(re.search(r"list=RD", url))
        label2 = "Whole playlist" if not is_mix else "Whole Mix (huge, hundreds of videos)"
        choice = ask("This link contains a playlist.", ["Just this one video", label2])
        playlist = choice == 2
        if playlist and is_mix:
            n = input("How many videos max? (Enter = 25): ").strip()
            args += ["--playlist-end", n if n.isdigit() else "25"]

    args.append("--yes-playlist" if playlist else "--no-playlist")

    kind = ask("What do you want?", ["Video", "Audio only (MP3)"])

    if kind == 1:
        q = ask("Quality?", ["Best available", "2160p (4K)", "1440p", "1080p", "720p", "480p"])
        heights = {2: 2160, 3: 1440, 4: 1080, 5: 720, 6: 480}
        if q in heights:
            h = heights[q]
            args += ["-f", f"bv*[height<={h}]+ba/b[height<={h}]"]
        args += ["--merge-output-format", "mp4"]
    else:
        args += ["-x", "--audio-format", "mp3", "--audio-quality", "0"]

    DEFAULT_OUT.mkdir(parents=True, exist_ok=True)
    name = "%(playlist_index)s - %(title)s [%(id)s].%(ext)s" if playlist else "%(title)s [%(id)s].%(ext)s"
    args += ["-P", str(DEFAULT_OUT), "-o", name, url]

    print(f"\nSaving to: {DEFAULT_OUT}\n")
    run_ytdlp(args)
    print("\nDone.")


def main():
    ensure_tools()
    while True:
        choice = ask("YT Downloader", ["Download", "Update yt-dlp", "Open downloads folder", "Quit"])
        if choice == 1:
            download_flow()
        elif choice == 2:
            run_ytdlp(["-U"])
        elif choice == 3:
            DEFAULT_OUT.mkdir(parents=True, exist_ok=True)
            os.startfile(DEFAULT_OUT)
        else:
            sys.exit(0)


if __name__ == "__main__":
    main()