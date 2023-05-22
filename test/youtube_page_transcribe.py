if __name__ == '__main__':
    from AutoSub.helper import set_proxy
    from AutoSub.transcribe import transcribe

    # For Chinese users, you might need a proxy for youtube.
    set_proxy("127.0.0.1", "7890")

    # Use chatgpt for transcription. (recommended)
    transcribe("https://www.youtube.com/watch?v=vwHqxe9eVMk&list=PLA5yNsxyt7sC3B4qhj_sMgGWqWWaSerq-", mode='chat')

    # Use davinci for transcription.
    # transcribe("https://www.youtube.com/watch?v=vwHqxe9eVMk&list=PLA5yNsxyt7sC3B4qhj_sMgGWqWWaSerq-", mode='complete')

