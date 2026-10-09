# %%
import os
import subprocess
import sys

import yt_dlp

# %%


def sanitize_filename(title: str) -> str:
    invalid_chars = '<>:"/\\|?*'
    cleaned = ''.join('_' if char in invalid_chars else char for char in title)
    cleaned = cleaned.strip().rstrip('.')
    return cleaned or 'downloaded_audio'


def open_file(path: str) -> None:
    if os.name == 'nt':
        os.startfile(path)
    elif sys.platform == 'darwin':
        subprocess.Popen(['open', path])
    else:
        subprocess.Popen(['xdg-open', path])


def run():
    # Ask the user for the video they want to download
    video_url = input("Please enter the YouTube Video URL: ").strip()
    if not video_url:
        raise ValueError("A video URL is required.")

    # Download metadata without immediately downloading the file
    with yt_dlp.YoutubeDL({'noplaylist': True, 'quiet': True}) as ydl:
        video_info = ydl.extract_info(video_url, download=False)

    video_title = video_info.get('title') if isinstance(video_info, dict) else None
    if not video_title:
        raise RuntimeError(
            "Could not retrieve the video's title. Check the URL and try again."
        )

    safe_title = sanitize_filename(video_title)
    filename = f"{safe_title}.mp3"

    # Ask the user for the path they want to save the file after it has been downloaded
    path_to_save = input(
        r"Enter where the file is to be saved or leave empty if you want it to be saved in the current working directory: "
    ).strip()

    where_to_save = os.getcwd()
    if path_to_save:
        where_to_save = os.path.abspath(path_to_save)

    os.makedirs(where_to_save, exist_ok=True)

    output_path = os.path.join(where_to_save, filename)
    output_template = os.path.join(where_to_save, f"{safe_title}.%(ext)s")

    options = {
        'quiet': True,
        'noplaylist': True,
        'format': 'bestaudio/best',
        'keepvideo': False,
        'outtmpl': output_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([video_info.get('webpage_url', video_url)])

    if os.path.exists(output_path):
        open_file(output_path)
    else:
        raise FileNotFoundError(f"The file could not be created: {output_path}")


if __name__ == '__main__':
    run()
