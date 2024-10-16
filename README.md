Created a web-based audio equalizer that allows users to upload or record audio and adjust four distinct frequency bands—Bass, Mid-Low, Mid-High, and Treble—using gain controls
to modify the sound in real-time. The equalizer implements Butterworth filters for precise frequency filtering.
Built with Python and Flask for the backend, the project efficiently handles real-time audio processing using NumPy and SciPy for digital signal processing.
PyAudio manages audio recording and playback, while Pydub enables file format conversion.
The application leverages threading to ensure smooth and responsive user interaction during tasks like audio recording, playback, and filter application. 
Additionally, users can clean audio tracks by reducing unwanted noise in specific frequency bands.


How to use:
1.	Record your audio or upload a sound file.
2.	Press “Play” to listen to the original track.
3.	Adjust the gain sliders to your preferred levels.
4.	Click “Apply Filters” to apply the equalizer settings.
5.	Press “Play” to hear the modified audio.
Note:	You can stop playback at any time by pressing “Stop Playback.”
