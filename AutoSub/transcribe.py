import concurrent.futures
from tqdm import tqdm
from openai_tasks import *
from AutoSub import DEBUG, translation_path, media_path, output_path, max_concurrent_request
from youtube_downloader import download_page
from helper import *
from whisper_task import transcribe_cached
from srt_tools import Subtitles


def transcribe(youtube_video_url, mode='chat'):
    # Step 1 : Download.
    title, audio_path, video_path = download_page(youtube_video_url, media_path)

    # Step 2 : Whisper transcription.
    output = transcribe_cached(title, audio_path)

    # Step 3 : Merge words into srt:
    words = []
    for segment in output['segments']:
        words.extend(segment['words'])
    input_subtitle = Subtitles()
    sentence_idx = 0
    cur_sentence = ''
    s_st = 0
    s_et = 0
    for word in words:
        cur_sentence += word['word']
        s_et = word['end']
        if is_eos(word['word'].strip()[-1]):
            input_subtitle.add_line(subtitle_number=sentence_idx, text=cur_sentence, start_time=s_st, end_time=s_et)
            cur_sentence = ''
            s_st = s_et
            sentence_idx += 1
    if cur_sentence != '':
        input_subtitle.add_line(subtitle_number=sentence_idx, text=cur_sentence, start_time=s_st, end_time=s_et)


    # Step 4 : Async bulk translation.
    responses = []
    to_be_translated = Subtitles()
    executor = concurrent.futures.ProcessPoolExecutor(max_workers=max_concurrent_request, initializer=set_proxy,
                                                      initargs=("127.0.0.1", "7890"))

    if DEBUG:
        input_subtitle.lines = input_subtitle.lines[:20]

    for line in input_subtitle.lines:
        if (line.end_time - to_be_translated.start_time(default=line.end_time) > max_time) or \
                (len(enc.encode(line.text)) + len(enc.encode(str(to_be_translated))) > max_token):
            wait_time = max_concurrent_request * 60.0 * \
                        max(len(enc.encode(str(to_be_translated))) / rate_limits[mode]['TPM'],
                            1 / rate_limits[mode]['RPM'])  # RPM limiter.

            responses.append(executor.submit(process_bulk, mode, to_be_translated, title, wait_time))
            to_be_translated = Subtitles()

        to_be_translated.add_subline(line)

    if len(to_be_translated.lines) != 0:
        responses.append(executor.submit(process_bulk, mode, to_be_translated, title, 0))

    # Step 5 : Sync collect responses.
    if not os.path.exists(translation_path):
        os.makedirs(translation_path)
    sub_path = os.path.join(translation_path, make_valid_linux_filename(title) + '.srt')
    with open(sub_path, 'w', encoding='utf-8') as file:
        logger.info("Dumping translation to " + file.name)
        for f in tqdm(responses):
            try:
                file.write(str(f.result()))
            except:
                logger.warn(title + " translation is not complete, run again later.")
        logger.info("Translation is dumped to " + file.name)

    if not os.path.exists(output_path):
        os.makedirs(output_path)
    merge_mkv(video_file=video_path, audio_file=audio_path, subtitle_file=sub_path,
              output_file=os.path.join(output_path, make_valid_linux_filename(title) + '.mkv'))


if __name__ == '__main__':
    from pytube import Playlist

    set_proxy("127.0.0.1", "7890")
    playlist = Playlist("https://www.youtube.com/playlist?list=PLA5yNsxyt7sC3B4qhj_sMgGWqWWaSerq-")
    playlist = list(playlist.video_urls)[3:4]

    for video_url in playlist:
        transcribe(video_url)
