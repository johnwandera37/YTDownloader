# YTDownloader

A simple Windows tool for downloading YouTube videos and audio with a numbered menu. No commands to remember: run it, pick options by number, done.

Built by **johnwanderaOrg**. It is a friendly front end for [yt-dlp](https://github.com/yt-dlp/yt-dlp), [FFmpeg](https://github.com/yt-dlp/FFmpeg-Builds) and [Deno](https://deno.com).

> For downloading content you have the right to download. You are responsible for following YouTube's Terms of Service and copyright law.

## What it does

- Downloads a single video or a whole playlist
- Lets you choose quality: best available, 4K, 1440p, 1080p, 720p or 480p
- Saves audio only as MP3
- Merges video and audio into one `.mp4` file
- Warns you about YouTube Mixes (links with `list=RD...`), which are endless, and caps them at 25 videos by default
- Skips the playlist question when the link is a plain video
- Has an **Update yt-dlp** menu option, which is the fix when downloads start failing

Files are saved to `Downloads\YTDownloader`.

## Using it

1. Download `YTDownloader.exe` from the [Releases](../../releases) page.
2. Run it. On first launch it downloads yt-dlp, FFmpeg and Deno (about 230 MB, one time only).
3. Paste a link and answer the numbered prompts.

If setup is interrupted, just run it again and it will pick up the missing tools.

### Portable use (USB stick)

Copy `YTDownloader.exe` and the `bin` folder from `%LOCALAPPDATA%\YTDownloader` into the same folder. The app uses the `bin` folder next to the exe and skips the download.

### Antivirus or SmartScreen warnings

The exe is unsigned and built with PyInstaller, so Windows or your antivirus may flag it. Choose **More info > Run anyway**, or restore it from quarantine and add an exclusion.

## Building from source

Run these in Windows (PowerShell), not WSL. PyInstaller builds for the OS it runs on.

```powershell
python --version
pip install pyinstaller
cd C:\path\to\folder\with\app.py
pyinstaller --onefile --name YTDownloader app.py
```

The exe appears in `dist\YTDownloader.exe`. If antivirus complains, try `--onedir` instead of `--onefile`.

## Troubleshooting

- **Downloads fail or error out:** choose **Update yt-dlp** from the menu. YouTube changes often and yt-dlp ships fixes quickly.
- **Want fresh FFmpeg or Deno:** delete their exes from the `bin` folder and relaunch.
- **Window closes instantly:** run the exe from PowerShell to see the error.

## Roadmap

- Paste multiple links
- Custom output folder
- Subtitle download
