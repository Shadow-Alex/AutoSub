import openai, os, re, subprocess
from AutoSub import logger


# helper function: parse hostip for wsl2.
def get_host_ip():
    import subprocess
    output = subprocess.check_output("cat /etc/resolv.conf | grep nameserver | awk '{ print $2 }'", shell=True)
    output = output.decode("utf-8").rstrip()
    return output


# helper function: end of sentence check.
def is_eos(char):
    eos = "!.?"
    return char in eos


# helper funtion: proxy settings
def set_proxy(hostip="127.0.0.1", port="7890"):
    host_ip = hostip
    openai.proxy = {
        'http': host_ip + ":" + port,
        'https': host_ip + ":" + port
    }
    os.environ['http_proxy'] = "http://" + host_ip + ":" + port
    os.environ['https_proxy'] = "https://" + host_ip + ":" + port


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

def merge_mkv(video_file, audio_file, subtitle_file, output_file):
    logger.info("Merging files into " + output_file)
    logger.debug("ffmpeg -i " + video_file + " -i " + audio_file + " -i " + subtitle_file + ' -c copy ' + output_file)
    subprocess.run("ffmpeg -i " + video_file + " -i " + audio_file + " -i " + subtitle_file + ' -c copy ' + output_file)

