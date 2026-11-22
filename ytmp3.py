import os
import subprocess
import sys
from typing import List
import yt_dlp


def sanitize_filename(title: str) -> str:
    # removes all invalid characters for filenames in Windows, macOS, and Linux
    invalid_chars = '<>:"/\\|?*'
    cleaned = ''.join('_' if char in invalid_chars else char for char in title)
    cleaned = cleaned.strip().rstrip('.')
    return cleaned or 'downloaded_audio'


def open_folder_or_file(path: str) -> None:
    
    try:
        if os.name == 'nt':
            os.startfile(path)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])
    except Exception as e:
        print(f"error to open path: ({path}): {e}")


def collect_urls() -> List[str]:
    # user needs to input the urls
    urls = []
    print("paste youtube link one per line and press enter")
    print("if you are finished press enter on an epmpty line\n")

    while True:
        prompt = f"Link {len(urls) + 1} (or press enter to start): "
        url = input(prompt).strip()
        
        if not url:
            break
            
        if url in urls:
            print("this link as arleady been entered and will be skipped")
            continue
            
        urls.append(url)

    return urls


def download_single_audio(video_url: str, where_to_save: str, index: int, total: int) -> bool:
    # function to download the video and converti it in mp3
    print(f"\n[{index}/{total}] gaining information for: {video_url}")
    
    try:
        # metadata extrraction 
        with yt_dlp.YoutubeDL({'noplaylist': True, 'quiet': True, 'no_warnings': True}) as ydl:
            video_info = ydl.extract_info(video_url, download=False)

        if not isinstance(video_info, dict) or not video_info.get('title'):
            print(f"impossible to obtain title for: {video_url}")
            return False

        video_title = video_info['title']
        safe_title = sanitize_filename(video_title)
        filename = f"{safe_title}.mp3"
        output_path = os.path.join(where_to_save, filename)
        output_template = os.path.join(where_to_save, f"{safe_title}.%(ext)s")

        # file check
        if os.path.exists(output_path):
            print(f"file '{filename}' arleady exist, download will be skipped")
            return True

        print(f"downloading '{video_title}' ...")

        # yt-dlp and ffmpeg configuration
        options = {
            'quiet': True,
            'no_warnings': True,
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

        # 3. Esecuzione del download e conversione
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([video_info.get('webpage_url', video_url)])

        if os.path.exists(output_path):
            print(f"completed: {filename}")
            return True
        else:
            print(f"error: couldn't generate file for: '{video_title}'.")
            return False

    except yt_dlp.utils.DownloadError as e:
        print(f"download error for: {video_url}: {e}")
        return False
    except Exception as e:
        print(f"unexpected error during processing of: {video_url}: {e}")
        return False


def run():
    # link collection
    urls = collect_urls()
    
    if not urls:
        print("\nno link given, exiting...")
        return

    print(f"\n {len(urls)} link have been inserted")

    # directory input
    path_to_save = input(
        "\ninsert the download directory, or press enter to use the current directory: "
    ).strip()

    where_to_save = os.path.abspath(path_to_save) if path_to_save else os.getcwd()
    os.makedirs(where_to_save, exist_ok=True)
    print(f"files will be saved in {where_to_save}")

    # queue processing
    successful = 0
    failed = 0

    for idx, url in enumerate(urls, start=1):
        if download_single_audio(url, where_to_save, idx, len(urls)):
            successful += 1
        else:
            failed += 1

    print("\n" + "=" * 40)
    print(f"succeffully downloaded: {successful}")
    print(f"failed: {failed}")
    print("=" * 40)

    # directory opening
    if successful > 0:
        open_folder = input("\ndo you want to open the folder? (y/n): ").strip().lower()
        if open_folder in ('s', 'si', 'sì', 'y', 'yes', ''):
            open_folder_or_file(where_to_save)


if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        print("\n\nprocess manually intterupted by user")
        sys.exit(0)
