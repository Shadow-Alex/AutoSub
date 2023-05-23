import openai
import tiktoken
from AutoSub import DEBUG, MODE, logger
from time import sleep
from srt_tools import Subtitles

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
def translate_bulk(mode, to_be_translated, context_prompt, temp=0.0):
    # prompt engineering.
    to_be_translated = "This is a transcript srt file from " + \
                       "\"" + context_prompt + "\", 请你翻译为中文，请注意输出必须保持为字幕srt格式:\n" + str(to_be_translated)

    if mode == "chat":
        return openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": to_be_translated}
            ],
            stream=True,
            temperature=temp,
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


def process_bulk(mode, to_be_translated, title, idle_time):
    cur_temp = 0  # if chatgpt made a mistake, raise tempreture and request again.
    while True:
        try:
            sleep(idle_time)
            response = translate_bulk(mode, to_be_translated, title, cur_temp)
            out = ''
            if mode == 'chat':
                for item in response:
                    try:
                        out += item['choices'][0]['delta']['content']
                    except:
                        pass  # "finish reason stop." or " assistance @ beginning."
            elif mode == 'complete':
                for item in response:
                    try:
                        out += item['choices'][0]['text']
                    except:
                        pass

            # sanity checks:
            # check 1 : valid srt.
            try:
                translation = Subtitles.from_str(out)
            except Exception as e:
                logger.info("Translation sanity check 1 failed. Raise temperature and try again later.")
                logger.debug("Sanity check 1 error msg : " + str(e))
                logger.debug("input_srt is : " + str(to_be_translated))
                cur_temp += 0.1
                idle_time = max(1, idle_time * 2)
                continue

            # check 2 : resemble input.
            if not translation.resemble(to_be_translated):
                logger.info("Translation sanity check 2 failed. Raise temperature and try again later.")
                if cur_temp == 0.3:
                    raise Exception("API is so stupid.")
                else:
                    cur_temp += 0.1
                    idle_time = max(1, idle_time * 2)
                    continue

            return translation

        except openai.error.RateLimitError or openai.error.APIError:
            if idle_time > 32:
                raise Exception("API connection is so bad.")

            logger.info("API is busy, will try again later.")
            idle_time = max(4, idle_time * 2)