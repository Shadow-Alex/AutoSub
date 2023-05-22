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

## Cost projection
This project run openai whisper locally to save your wallet. So the cost is solely text API.
A typical english class for 1 hour sums up around 10~15K tokens, and a 15~25K for
the translation depends on output language. If you are using 'chat' mode, this means around 0.05~0.08 USD.


## Project history
* v1.0 : A stable version for Chinese translation.