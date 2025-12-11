import moviepy.editor as mp
import os

def extract_audio(video_path, output_path="temp_audio.wav"):
    try:
        video = mp.VideoFileClip(video_path)
        video.audio.write_audiofile(output_path, logger=None)
        return output_path
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return None

def clean_up(paths):
    for p in paths:
        if os.path.exists(p):
            os.remove(p)