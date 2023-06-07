import os
from pytube import YouTube
import re
import openai

with open('openai_key.txt', 'r') as f:
    api_key = f.read().strip('\n')
    assert api_key.startswith('sk-'), "Please enter a valid OpenAI API key"
openai.api_key = api_key

def youtube_audio_downloader(link):
    if "youtube.com" not in link:
        print("Please enter a valid YouTube URL")
        return False
    yt = YouTube(link)
    print(f'Title of the video: {yt.title}')
    print(f'Length of the video: {yt.length} seconds')

    audio_stream = yt.streams.filter(only_audio=True).first()
    download_result = audio_stream.download(
        output_path='audios',
    )

    if (os.path.exists(download_result)):
        print("File downloaded successfully")
    else:
        print("Some error occurred")
        return False

    basename = os.path.basename(download_result)

    name, extension = os.path.splitext(basename)
    audio_file = re.sub('\s+', '-', name)
    complete_audio_path = f'{audio_file}.mp3'
    os.rename(download_result, complete_audio_path)
    return complete_audio_path


def transcribe(audio_file, not_english=False):
    if not os.path.exists(audio_file):
        print(f'The following file does not exist: {audio_file}')
        return False

    if not_english:
        with open(audio_file, 'rb') as f:
            print("Translating non-English audio to English ...", end='')
            transcript = openai.Audio.translate('whisper-1', f)
            print('Done!')

    else:
        with open(audio_file, 'rb') as f:
            print("Transcribing Started ...", end='')
            transcript = openai.Audio.transcribe('whisper-1', f)
            print('Done!')

    name, extension = os.path.splitext(audio_file)
    transcript_filename = f'transcript-{name}.txt'
    with open(transcript_filename, 'w') as f:
        f.write(transcript['text'])

    return transcript_filename


def summarize(transcript_filename):
    if not os.path.exists(transcript_filename):
        print("The transcript file doesn't exist!")
        return False

    with open(transcript_filename) as f:
        transcript = f.read()

    system_prompt = "Act as Expert one who can summarize any topic"
    prompt = f'''Create a summary of the following text.
    Text{transcript}

    Add a title to the summary.
    Your summary should be informative and factual, covering the most important aspects of the topic.
    Use BULLET POINTS if possible'''

    print("Summarizing Started....", end=" ")

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': prompt}
        ],
        max_tokens=2024,
        temperature=1

    )

    print('Done!')
    r = response['choices'][0]['message']['content']
    return r


link = input("Enter a YouTube link: ")
downloaded_audio_file = youtube_audio_downloader(link)
transcribed_file = transcribe(downloaded_audio_file, not_english=False)
summary = summarize(transcribed_file)
print('\n')
print(summary)
