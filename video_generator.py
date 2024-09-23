import os
import numpy as np
import librosa
import matplotlib.pyplot as plt
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, VideoClip
from moviepy.video.io.bindings import mplfig_to_npimage
from PIL import Image, ImageDraw, ImageFont
import readline
import argparse
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import functools

# Optimization 1: Use a lower sample rate for audio processing
SAMPLE_RATE = 22050  # Lower sample rate (default is usually 44100)

# Optimization 2: Reduce the number of mel bands for faster processing
N_MELS = 64  # Reduced from the default 128

# Optimization 4: Cache size for audio visualization frames
CACHE_SIZE = 100

def create_audio_visualization(audio_path, duration, wave_color, progress_callback=None):
    if progress_callback:
        progress_callback(10)
    print(f"Loading audio file: {audio_path}")
    try:
        # Optimization 1: Load audio with lower sample rate
        y, sr = librosa.load(audio_path, sr=SAMPLE_RATE)
        if progress_callback:
            progress_callback(20)
        print(f"Audio loaded successfully. Sample rate: {sr}, Length: {len(y)}")
        
        # Optimization 2: Use a smaller n_fft and hop_length for faster STFT
        n_fft = 1024
        hop_length = 512
        D = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
        mag, _ = librosa.magphase(D)
        
        # Optimization 2: Use fewer mel bands
        mel = librosa.feature.melspectrogram(S=mag, sr=sr, n_mels=N_MELS)
        mel_db = librosa.power_to_db(mel, ref=np.max)
        if progress_callback:
            progress_callback(30)
        print("Audio processing completed successfully")
    except Exception as e:
        print(f"Error processing audio file: {str(e)}")
        raise

    # Optimization 3: Pre-compute angles for faster frame generation
    angles = np.linspace(0, 2*np.pi, num=N_MELS, endpoint=False)

    # Optimization 4: Implement frame caching
    @functools.lru_cache(maxsize=CACHE_SIZE)
    def make_frame_cached(t):
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        time_index = int(t * sr / hop_length)
        values = mel_db[:, time_index] + 40
        
        ax.bar(angles, values, color=wave_color, alpha=0.8, width=2*np.pi/N_MELS)
        
        ax.set_ylim(0, 80)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.spines['polar'].set_visible(False)
        fig.patch.set_alpha(0)
        ax.set_facecolor('none')
        
        img = mplfig_to_npimage(fig)
        plt.close(fig)
        return img

    # Create circular audio visualization with bars
    def make_frame(t):
        return make_frame_cached(round(t, 2))  # Round to 2 decimal places for better caching

    return VideoClip(make_frame, duration=duration)

def create_text_clip(text, font_path, font_size, color, stroke_color, stroke_width, size):
    # Optimization 5: Create text image only once
    img = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, font_size)
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    text_width = right - left
    text_height = bottom - top
    position = ((size[0] - text_width) / 2, (size[1] - text_height) / 2)

    for adj in range(-stroke_width, stroke_width+1):
        for opp in range(-stroke_width, stroke_width+1):
            draw.text((position[0]+adj, position[1]+opp), text, font=font, fill=stroke_color)

    draw.text(position, text, font=font, fill=color)
    return ImageClip(np.array(img))

def generate_video(audio_path, image_path, heading_text, font, heading_color, outline_color, wave_color, output_path, progress_callback=None, log_callback=None):
    try:
        audio_path = os.path.expanduser(audio_path)
        image_path = os.path.expanduser(image_path)

        if log_callback:
            log_callback(f"Audio path: {audio_path}")
            log_callback(f"Image path: {image_path}")
        else:
            print(f"Audio path: {audio_path}")
            print(f"Image path: {image_path}")

        if not os.path.exists(audio_path):
            raise ValueError(f"Audio file not found: {audio_path}")
        if not os.path.exists(image_path):
            raise ValueError(f"Background image not found: {image_path}")
        if not heading_text:
            raise ValueError("Heading text is required")

        if log_callback:
            log_callback("Loading audio file...")
        else:
            print("Loading audio file...")
        audio = AudioFileClip(audio_path)
        audio_duration = audio.duration
        if log_callback:
            log_callback(f"Audio duration: {audio_duration}")
        else:
            print(f"Audio duration: {audio_duration}")

        if log_callback:
            log_callback("Creating background...")
        else:
            print("Creating background...")
        background = ImageClip(image_path).set_duration(audio_duration)
        if progress_callback:
            progress_callback(40)

        if log_callback:
            log_callback("Creating audio visualization...")
        else:
            print("Creating audio visualization...")
        audio_vis = create_audio_visualization(audio_path, audio_duration, wave_color, progress_callback)
        if progress_callback:
            progress_callback(60)

        if log_callback:
            log_callback("Creating heading text...")
        else:
            print("Creating heading text...")
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Adjust this path if needed
        heading = create_text_clip(heading_text, font_path, 70, heading_color, outline_color, 2, background.size)
        heading = heading.set_duration(audio_duration)
        if progress_callback:
            progress_callback(70)

        if log_callback:
            log_callback("Composing video...")
        else:
            print("Composing video...")
        video = CompositeVideoClip([background, audio_vis, heading.set_position(('center', 50))])
        video = video.set_audio(audio)
        if progress_callback:
            progress_callback(80)

        if log_callback:
            log_callback(f"Writing video file to {output_path}...")
        else:
            print(f"Writing video file to {output_path}...")
        
        # Optimization 6: Adjust video writing parameters
        n_threads = max(multiprocessing.cpu_count() - 1, 1)  # Use all available cores except one
        video.write_videofile(output_path, fps=24, threads=n_threads, audio_codec='aac', 
                              bitrate='5000k', preset='faster', ffmpeg_params=['-crf', '23'])
        
        if progress_callback:
            progress_callback(100)
        if log_callback:
            log_callback(f"Video generated successfully: {output_path}")
        else:
            print(f"Video generated successfully: {output_path}")

    except Exception as e:
        if log_callback:
            log_callback(f"Error: {str(e)}")
        else:
            print(f"Error: {str(e)}")

def path_completer(text, state):
    """
    This is the autocomplete function for paths.
    """
    # Expand ~ to the user's home directory
    if text.startswith('~'):
        text = os.path.expanduser(text)

    # Get the dirname of the path
    dirname = os.path.dirname(text)

    # If dirname is empty, use current directory
    if not dirname:
        dirname = '.'

    # Get a list of files in the directory
    try:
        files = os.listdir(dirname)
    except OSError:
        return None

    # Add '/' to directories
    files = [f + '/' if os.path.isdir(os.path.join(dirname, f)) else f for f in files]

    # Filter matching files
    matches = [f for f in files if f.startswith(os.path.basename(text))]

    try:
        return matches[state]
    except IndexError:
        return None

def setup_autocomplete():
    """
    Set up the readline completer for path autocomplete.
    """
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(path_completer)

def input_with_autocomplete(prompt):
    """
    Custom input function that uses readline for autocomplete.
    """
    setup_autocomplete()
    return input(prompt)

def prompt_for_missing_args(args):
    """
    Prompt the user for any missing required arguments.
    """
    if not args.audio_path:
        args.audio_path = input_with_autocomplete("Enter the path to the audio file: ")
    if not args.image_path:
        args.image_path = input_with_autocomplete("Enter the path to the background image: ")
    if not args.heading_text:
        args.heading_text = input("Enter the text to display as heading: ")
    if not args.font:
        args.font = input("Enter the font for the heading text (default: Arial): ") or "Arial"
    if not args.heading_color:
        args.heading_color = input("Enter the color of the heading text (default: #FFFFFF): ") or "#FFFFFF"
    if not args.outline_color:
        args.outline_color = input("Enter the color of the heading text outline (default: #000000): ") or "#000000"
    if not args.wave_color:
        args.wave_color = input("Enter the color of the audio wave (default: #FF0000): ") or "#FF0000"
    if not args.output_path:
        args.output_path = input_with_autocomplete("Enter the output video file path (default: output.mp4): ") or "output.mp4"
    return args

def main():
    parser = argparse.ArgumentParser(description="Generate a video with audio visualization and text overlay.")
    parser.add_argument("--audio_path", help="Path to the audio file")
    parser.add_argument("--image_path", help="Path to the background image")
    parser.add_argument("--heading_text", help="Text to display as heading")
    parser.add_argument("--font", default="Arial", help="Font for the heading text")
    parser.add_argument("--heading_color", default="#FFFFFF", help="Color of the heading text")
    parser.add_argument("--outline_color", default="#000000", help="Color of the heading text outline")
    parser.add_argument("--wave_color", default="#FF0000", help="Color of the audio wave")
    parser.add_argument("--output_path", default="output.mp4", help="Output video file path")

    args = parser.parse_args()
    args = prompt_for_missing_args(args)

    generate_video(
        args.audio_path,
        args.image_path,
        args.heading_text,
        args.font,
        args.heading_color,
        args.outline_color,
        args.wave_color,
        args.output_path
    )

if __name__ == "__main__":
    main()