import os

import whisper
from tqdm import tqdm
from openai_tasks import *
from AutoSub import DEBUG, translation_path, media_path, logger
from youtube_downloader import download_page
from helper import *

def load_model():
    return whisper.load_model('tiny', device='cuda') if DEBUG else whisper.load_model('large-v2', device='cuda')


def transcribe(youtube_video_url, mode='chat'):
    # Step 1 : Download.
    title, stored_path = download_page(youtube_video_url, media_path)
    model = load_model()

    # Step 2 : Whisper transcription.
    output = model.transcribe(stored_path, initial_prompt="This is " + title + "\n", verbose=True, language='en',
                              word_timestamps=True)

    # Step 3 : Merge words into sentences:
    words = []
    for segment in output['segments']:
        words.extend(segment['words'])
    sentences = []
    cur_sentence = ''
    s_st = 0
    s_et = 0
    for word in words:
        cur_sentence += word['word']
        s_et = word['end']
        if is_eos(word['word'].strip()[-1]):
            sentences.append({'text': cur_sentence, 'start': s_st, 'end': s_et, 'tokens': enc.encode(cur_sentence)})
            cur_sentence = ''
            s_st = s_et
    if cur_sentence != '':
        sentences.append({'text': cur_sentence, 'start': s_st, 'end': s_et, 'tokens': enc.encode(cur_sentence)})

    # Step 4 : Async bulk translation.
    to_be_translated = ''
    token_cnt = 0
    start_time = 0
    end_time = 0
    responses = []

    if DEBUG:
        sentences = sentences[:30]

    for idx, segment in enumerate(sentences):
        if (segment['end'] - start_time > max_time) or (len(segment['tokens']) + token_cnt > max_token):
            responses.append(process_bulk(mode, to_be_translated, start_time, end_time, title))
            # rate limit
            sleep(4 * 60.0 * max(token_cnt / rate_limits[mode]['TPM'],
                                 1 / rate_limits[mode]['RPM']))  # aggressive : 1.1x works too.

            to_be_translated = ''
            token_cnt = 0
            start_time = end_time

        token_cnt += len(segment['tokens']) + len(enc.encode('9999\nHH:MM:SS.mmm --> HH:MM:SS.mmm\n'))
        to_be_translated = to_be_translated + \
                           str(idx + 1) + '\n' + \
                           convert_second(segment['start']) + ' --> ' + convert_second(segment['end']) + '\n' + \
                           segment['text'].strip() + '\n\n'

        end_time = segment['end']

    if to_be_translated != '':
        responses.append(process_bulk(mode, to_be_translated, start_time, end_time, title))

    # Step 5 : Sync collect responses.
    for idx, item in tqdm(enumerate(responses)):
        generator = item['generator']
        mode = item['mode']

        out = ''
        if mode == 'chat':
            for item in generator:
                try:
                    out += item['choices'][0]['delta']['content']
                except:
                    pass  # "finish reason stop." or " assistance @ beginning."
        elif mode == 'complete':
            for item in generator:
                try:
                    out += item['choices'][0]['text']
                except:
                    pass
        responses[idx]['out'] = out

    if not os.path.exists(translation_path):
        os.makedirs(translation_path)

    with open(os.path.join(translation_path, make_valid_linux_filename(title) + '.txt'), 'w') as file:
        print("Transcription is dumped to " + file.name)
        for idx, item in enumerate(responses):
            file.write(item['out'] + "\n")