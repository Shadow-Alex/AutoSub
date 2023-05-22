import whisper
import os, pickle
from AutoSub import DEBUG, transcription_path, logger
from helper import make_valid_linux_filename


def load_model():
    return whisper.load_model('tiny', device='cuda') if DEBUG else whisper.load_model('large-v2', device='cuda')


def transcribe_cached(video_title, audio_path):
    transcription_file = os.path.join(transcription_path, make_valid_linux_filename(video_title) + '.pickle')
    if not os.path.exists(transcription_file):
        model = load_model()
        logger.info("Transcribing " + video_title)
        output = model.transcribe(audio_path, initial_prompt="This is " + video_title + "\n", verbose=True,
                                  language='en', word_timestamps=True)

        if not os.path.exists(transcription_path):
            os.makedirs(transcription_path)
        with open(transcription_file, 'wb') as file:
            pickle.dump(output, file)
            logger.info("Transcription of " + video_title + " is saved to " + transcription_file)

    else:
        logger.info("Cached transcription of " + video_title + " is found at " + transcription_file)
        with open(transcription_file, 'rb') as file:
            output = pickle.load(file)

    return output
