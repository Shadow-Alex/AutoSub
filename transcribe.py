# import whisper
import whisper
from pytube import YouTube
import os
import openai
from time import sleep
from tqdm import tqdm
import tiktoken
import re

mode = 'chat'
debug = False
openai.api_key_path = 'openai.keys'
enc = tiktoken.encoding_for_model("gpt-3.5-turbo") if mode == 'chat' else tiktoken.encoding_for_model(
    "text-davinci-003")
audios = 'audios'
transcriptions = 'transcriptions/'

rate_limits = {
    'chat': {'RPM': 3500, 'TPM': 90000},
    'complete': {'RPM': 3000, 'TPM': 250000}
}
if debug:
    max_token = 500
else:
    max_token = 1500
max_time = 600


# helper function: parse hostip for wsl2.
def get_host_ip():
    import subprocess
    output = subprocess.check_output("cat /etc/resolv.conf | grep nameserver | awk '{ print $2 }'", shell=True)
    output = output.decode("utf-8").rstrip()
    return output


# helper function: generate valid linux filename from video title.
def make_valid_linux_filename(string):
    # Remove or replace invalid characters
    filename = re.sub(r"[^\w.-]", "_", string)

    # Ensure filename starts with a letter or underscore
    if not filename[0].isalpha() and filename[0] != "_":
        filename = "_" + filename

    # Limit filename length if needed
    max_length = 255
    if len(filename) > max_length:
        filename = filename[:max_length]

    return filename


# helper function : pytube download audio
def download_audio(youtube_video_url, dump_path):
    youtube_video = YouTube(youtube_video_url)
    print("Downloading audio " + youtube_video.title + " from " + youtube_video_url)
    stored_path = youtube_video.streams.filter(only_audio=True).first().download(dump_path)
    print("Stored to " + stored_path)
    return youtube_video.title, stored_path


# async translation
def translate_bulk(mode, to_be_translated, context_prompt):
    # prompt engineering.
    to_be_translated = "This is a transcript srt file from " + \
                       "\"" + context_prompt + "\", 请你翻译为中文，请注意输出必须保持为字幕srt格式:\n" + to_be_translated
    if debug:
        print(to_be_translated)

    if mode == "chat":
        return openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": to_be_translated}
            ],
            stream=True,
            temperature=0,
        )

    elif mode == "complete":
        return openai.Completion.create(
            model="text-davinci-003",
            prompt=to_be_translated,
            temperature=0,
            max_tokens=4096 - max_token,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stream=True  # 十分重要！stream保活！！！
        )


def process_bulk(mode, to_be_translated, start_time, end_time, title):
    while True:
        stand_by_time = 1
        try:
            response = translate_bulk(mode, to_be_translated, title)
            return responses.append({
                'text': to_be_translated,
                'generator': response,
                'mode': mode,
                'start_time': start_time,
                'end_time': end_time
            })
        except openai.error.RateLimitError:
            if stand_by_time > 16:
                raise ConnectionError("Rate Limit Error, try again maybe.")
            sleep(stand_by_time)
            stand_by_time *= 2


def load_model():
    return whisper.load_model('tiny.en', device='cuda') if debug else whisper.load_model('medium.en', device='cuda')


# helper function: timeline .srt form
def convert_second(seconds):
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    always_include_hours = True
    hours_marker = f"{hours:02d}:" if always_include_hours or hours > 0 else ""
    return (
        f"{hours_marker}{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
    )


def is_eos(char):
    eos = "!.?"
    return char in eos


if __name__ == '__main__':
    # Audio preparation.
    host_ip = "127.0.0.1"
    openai.proxy = {
        'http': host_ip + ":7890",
        'https': host_ip + ":7890"
    }
    os.environ['http_proxy'] = "http://" + host_ip + ":7890"
    os.environ['https_proxy'] = "https://" + host_ip + ":7890"

    if debug:
        title = 'Breaking bad S02E01'
        stored_path = 'audios/output-audio.dts'
    else:
        youtube_video_url = "https://www.youtube.com/watch?v=lUUte2o2Sn8"
        title, stored_path = download_audio(youtube_video_url, audios)

    model = load_model()
    # whisper transcription.
    output = model.transcribe(stored_path, initial_prompt="This is " + title + "\n", verbose=True, language='en',
                              word_timestamps=True)

    # Reform words into sentences:
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

    # Bulk translation. in srt form.
    to_be_translated = ''
    token_cnt = 0
    start_time = 0
    end_time = 0
    responses = []

    if debug:
        sentences = sentences[:30]

    for idx, segment in enumerate(sentences):
        if (segment['end'] - start_time > max_time) or (len(segment['tokens']) + token_cnt > max_token):
            process_bulk(mode, to_be_translated, start_time, end_time, title)
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
        process_bulk(mode, to_be_translated, start_time, end_time, title)

    # collect responses.
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

    with open(transcriptions + make_valid_linux_filename(title) + '.txt', 'w') as file:
        print("Transcription is dumped to " + file.name)
        for idx, item in enumerate(responses):
            file.write(item['out'] + "\n")
