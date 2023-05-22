import openai
import tiktoken
from AutoSub import DEBUG, MODE
from time import sleep

openai.api_key_path = 'openai.keys'
enc = tiktoken.encoding_for_model("gpt-3.5-turbo") if MODE == 'chat' else tiktoken.encoding_for_model(
    "text-davinci-003")
rate_limits = {
    'chat': {'RPM': 3500, 'TPM': 90000},
    'complete': {'RPM': 3000, 'TPM': 250000}
}
max_token = 500 if DEBUG else 1500
max_time = 200 if DEBUG else 600


# async translation
def translate_bulk(mode, to_be_translated, context_prompt):
    # prompt engineering.
    to_be_translated = "This is a transcript srt file from " + \
                       "\"" + context_prompt + "\", 请你翻译为中文，请注意输出必须保持为字幕srt格式:\n" + to_be_translated
    if DEBUG:
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
            return {
                'text': to_be_translated,
                'generator': response,
                'mode': mode,
                'start_time': start_time,
                'end_time': end_time
            }
        except openai.error.RateLimitError:
            if stand_by_time > 16:
                raise ConnectionError("Rate Limit Error, try again maybe.")
            sleep(stand_by_time)
            stand_by_time *= 2
