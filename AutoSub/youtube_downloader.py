import os.path, re

from pytube import YouTube, Playlist, Channel
from AutoSub import logger
from helper import make_valid_linux_filename


# download the best quality audio from a youtube page.
def download_best_audio(url, store_path):
    # Create a YouTube object
    yt = YouTube(url)

    # Get all available streams
    streams = yt.streams.filter(only_audio=True)

    # Sort the streams by abr in descending order
    sorted_streams = sorted(streams, key=lambda stream: int(stream.abr[:-4]), reverse=True)

    # Choose the first stream from the sorted list
    stream = sorted_streams[0]

    # Download the audio, re-Download if file exists.
    logger.info("Downloading audio of " + yt.title + "from " + url)
    filename = make_valid_linux_filename(yt.title) + '.mp4'
    file_path = os.path.join(store_path, filename)

    if not os.path.exists(store_path):
        os.makedirs(store_path)
    if os.path.exists(file_path):
        os.remove(file_path)

    stream.download(store_path, filename=filename)
    logger.info("Stored to " + file_path)
    return file_path


# download the best quality video from a youtube page.
def download_best_video(url, store_path):
    # Create a YouTube object
    yt = YouTube(url)

    # Get all available streams
    streams = yt.streams.filter(only_video=True)

    # Sort the streams by resolution & fps in descending order
    sorted_streams = sorted(streams, key=lambda stream: (int(stream.resolution[:-1]), int(stream.fps)), reverse=True)

    # Choose the first stream from the sorted list
    stream = sorted_streams[0]

    # Download the video, re-Download if file exists.
    logger.info("Downloading video of " + yt.title + "from " + url)
    filename = make_valid_linux_filename(yt.title) + '.mp4'
    file_path = os.path.join(store_path, filename)

    if not os.path.exists(store_path):
        os.makedirs(store_path)
    if os.path.exists(file_path):
        os.remove(file_path)

    stream.download(store_path, filename=filename)
    logger.info("Stored to " + file_path)
    return file_path


# download from a single youtube page.
def download_page(url, store_root):
    yt = YouTube(url)

    if not os.path.exists(store_root):
        os.makedirs(store_root)

    a_path = os.path.join(store_root, 'audios')
    v_path = os.path.join(store_root, 'videos')

    downloaded_video = download_best_video(url, v_path)
    downloaded_audio = download_best_audio(url, a_path)

    return yt.title, downloaded_audio


# download from a youtube playlist.
def download_playlist(url, store_root='', start=None, end=None):
    p = Playlist(url)
    p = p.video_urls[start:end]

    for video_url in p:
        download_page(video_url, store_root)


def download_channel(url, store_root='', start=None, end=None):
    c = Channel(url)
    c = c.video_urls[start:end]

    for video_url in c:
        download_page(video_url, store_root)
