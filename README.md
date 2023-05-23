# AutoSub 自动字幕组

本项目期望使用 [openai whisper](https://github.com/openai/whisper) 与 openai text API 为生肉视频生成字幕。

This project aims to use the OpenAI Whisper and OpenAI Text API to generate subtitles for raw videos.

## Get started

1. An [openai API](https://openai.com/blog/openai-api) is required.
2. Create a file named `openai.keys' and paste your key.
3. run the following code to download & transcribe & translate a youtube course :) You Will get a `.srt` output.

```python
from AutoSub.transcribe import transcribe

# Use chatgpt for translation. (recommended)
transcribe("https://www.youtube.com/watch?v=vwHqxe9eVMk&list=PLA5yNsxyt7sC3B4qhj_sMgGWqWWaSerq-", mode='chat')

# Use davinci for translation.
# transcribe("https://www.youtube.com/watch?v=vwHqxe9eVMk&list=PLA5yNsxyt7sC3B4qhj_sMgGWqWWaSerq-", mode='complete')
```

## How AutoSub work
```text
         pytube            whisper                  LLMs                 ffmpeg
origin _ _ _ _ _ _ audio _ _ _ _ _ _ transcript _ _ _ _ _ _ subtitle _ _ _ _ _ _ _ .mkv
             |               ^                      ^                      ^
             |               | prompt engineering   | prompt engineering   |
             | _ _ info  _ _ | _ _ _ _ _ _ _ _ _ _ _|                      |  
             |                                                             |
             |                                                             |
             | _ _ video _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ |
```

### I. Rule-based stability boost
LLM models behaviors can be elusive. So AutoSub asks LLM to perform translation in an end-to-end
manner. (Instructions and chunked `.srt` files are provided, and LLM is asked to translate it into a new 
`.srt` in the target language)

### II. Topic-related prompt engineering

## Cost projection
This project run openai whisper locally to save your wallet. So the cost is solely text API.
A typical english class for 1 hour gets around 10K tokens, and 20K for
the translation depends on output language. This means **0.06/h USD** in 'chat' mode or 0.6 USD in 'complete' mode.


## Project history
* v1.0 : A stable version for Chinese translation.
* v1.0.1 : Use ffmpeg to merge media.

## TODO
* v1.0.2 : add multilingual translation support.
* v1.1 : add CLI support.