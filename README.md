# Custom Video Generator

This Python application provides an interactive interface for generating customized videos. Users can create videos with a background image, audio track, and customizable heading text with various styling options.

## Features

- Generate videos using audio files (MP3, WAV)
- Use custom background images (JPG, PNG)
- Add customizable heading text with font and color options
- Create circular audio wave visualization
- Produce video with audio-reactive visuals
- Graphical User Interface (GUI) for easy interaction
- Optimized performance for faster video generation

## Installation

1. Clone this repository or download the source code.

2. Make sure you have Python 3.7 or higher installed.

3. Install the required dependencies using pip:

```
pip install -r requirements.txt
```

## Usage

### Command Line Interface

To use the command-line version, run the script without any arguments:

```
python video_generator.py
```

The program will prompt you for the following information:

1. Path to the audio file (MP3 or WAV)
2. Path to the background image file (JPG or PNG)
3. Text to display as heading
4. Font for the heading text (optional, default: Arial)
5. Color of the heading text (optional, default: #FFFFFF)
6. Color of the heading text outline (optional, default: #000000)
7. Color of the audio wave (optional, default: #FF0000)
8. Output video file path (optional, default: output.mp4)

#### Example Usage:

When you run the script, you'll see prompts like this:

```
Welcome to the Interactive Video Generator!
Enter the path to the audio file: path/to/audio.mp3
Enter the path to the background image: path/to/background.jpg
Enter the text to display as heading: My Custom Video
Enter the font for the heading text (default: Arial): Times New Roman
Enter the color of the heading text (default: #FFFFFF): #00FF00
Enter the color of the heading text outline (default: #000000): 
Enter the color of the audio wave (default: #FF0000): #0000FF
Enter the output video file path (default: output.mp4): my_video.mp4
```

This will generate a video with the specified audio and background image, with the heading "My Custom Video" in green Times New Roman font, and a blue audio wave visualization.

### Graphical User Interface

To use the GUI version of the application, run the following command:

```
python gui.py
```

The GUI provides an easy-to-use interface with the following features:

1. File browser buttons for selecting audio and image files
2. Text input for the heading
3. Color picker buttons for heading text, outline, and wave colors
4. Progress bar to show video generation progress
5. Log output to display generation status and any errors

Simply fill in the required fields, choose your colors, and click the "Generate Video" button to create your custom video.

## Performance Optimizations

Recent updates have significantly improved the performance of video generation:

- Frame caching: Audio visualization frames are now cached, reducing redundant computations.
- Optimized text rendering: The heading text image is created once and reused, improving efficiency.
- Enhanced video writing: Adjusted parameters for faster encoding while maintaining quality.
- Improved memory usage: Balanced caching to optimize performance without excessive memory consumption.

These optimizations result in faster video generation times, especially for longer audio files.

## Dependencies

- numpy
- librosa
- matplotlib
- moviepy
- PyQt5 (for GUI version)

These dependencies are listed in the `requirements.txt` file and can be installed using pip.

## Note

This application requires a working installation of FFmpeg for video processing. Please ensure FFmpeg is installed and accessible in your system's PATH.

## Troubleshooting

If you encounter any issues with audio processing or video generation, please make sure all dependencies are correctly installed and that FFmpeg is properly set up on your system.

For any other problems or feature requests, please open an issue on the project's GitHub repository.