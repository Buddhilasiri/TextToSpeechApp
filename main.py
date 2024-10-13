import tkinter as tk
from tkinter import filedialog, messagebox
import pyttsx3
import time
import threading
from utils.pdf_reader import extract_text_from_pdf

# Initialize Text-to-Speech engine
engine = pyttsx3.init()

# Global variables
text = ""
current_word_index = 0  # Keeps track of the current position in the text
paused = False  # Keeps track of whether the reading is paused
tts_thread = None  # Thread for the TTS process

def read_aloud():
    """Read the text aloud with current settings in a separate thread."""
    global current_word_index, paused

    speed = speed_scale.get()
    words_per_pause = words_per_pause_scale.get()
    pause_duration = pause_duration_scale.get() / 1000  # Convert milliseconds to seconds
    engine.setProperty('rate', speed)

    words = text.split()

    while current_word_index < len(words):
        if paused:  # Check if we should pause
            break

        chunk = ' '.join(words[current_word_index:current_word_index + words_per_pause])
        engine.say(chunk)
        engine.runAndWait()
        current_word_index += words_per_pause
        time.sleep(pause_duration)

    enable_controls()  # Enable controls when reading is done

def start_reading_thread():
    """Start reading aloud in a separate thread."""
    global tts_thread, current_word_index, paused

    if text:
        current_word_index = 0  # Reset to the beginning of the text
        paused = False
        disable_controls()  # Disable controls while reading

        # Create a new thread for reading aloud
        tts_thread = threading.Thread(target=read_aloud)
        tts_thread.start()
    else:
        messagebox.showwarning("No File Selected", "Please upload a PDF file first.")

def pause_reading():
    """Pause the reading."""
    global paused
    paused = True
    enable_controls()

def resume_reading_thread():
    """Resume reading in a separate thread."""
    global paused, tts_thread

    if paused:
        paused = False
        disable_controls()  # Disable controls while reading
        # Create a new thread to resume reading
        tts_thread = threading.Thread(target=read_aloud)
        tts_thread.start()

def upload_pdf():
    """Allow user to select a PDF file and extract its text."""
    global text
    file_path = filedialog.askopenfilename(
        title="Select PDF", filetypes=[("PDF Files", "*.pdf")]
    )
    if file_path:
        text = extract_text_from_pdf(file_path)
        file_label.config(text=f"Loaded: {file_path.split('/')[-1]}")

def disable_controls():
    """Disable buttons during TTS process."""
    start_button.config(state=tk.DISABLED)
    pause_button.config(state=tk.NORMAL)
    resume_button.config(state=tk.NORMAL)

def enable_controls():
    """Enable buttons after TTS process."""
    start_button.config(state=tk.NORMAL)
    pause_button.config(state=tk.DISABLED)
    resume_button.config(state=tk.DISABLED)

# Setup GUI
root = tk.Tk()
root.title("PDF to Speech App")
root.geometry("400x400")

# File upload section
file_frame = tk.Frame(root)
file_frame.pack(pady=20)
file_label = tk.Label(file_frame, text="No PDF selected")
file_label.pack()
upload_button = tk.Button(file_frame, text="Upload PDF", command=upload_pdf)
upload_button.pack()

# Speed control
speed_frame = tk.Frame(root)
speed_frame.pack(pady=10)
speed_label = tk.Label(speed_frame, text="Reading Speed (Words per minute):")
speed_label.pack()
speed_scale = tk.Scale(speed_frame, from_=100, to_=300, orient="horizontal")
speed_scale.set(150)
speed_scale.pack()

# Words per pause control
words_per_pause_frame = tk.Frame(root)
words_per_pause_frame.pack(pady=10)
words_per_pause_label = tk.Label(words_per_pause_frame, text="Words per Pause:")
words_per_pause_label.pack()
words_per_pause_scale = tk.Scale(words_per_pause_frame, from_=1, to_=10, orient="horizontal")
words_per_pause_scale.set(5)
words_per_pause_scale.pack()

# Pause duration control
pause_duration_frame = tk.Frame(root)
pause_duration_frame.pack(pady=10)
pause_duration_label = tk.Label(pause_duration_frame, text="Pause Duration (milliseconds):")
pause_duration_label.pack()
pause_duration_scale = tk.Scale(pause_duration_frame, from_=100, to_=2000, orient="horizontal")
pause_duration_scale.set(500)
pause_duration_scale.pack()

# Control buttons
controls_frame = tk.Frame(root)
controls_frame.pack(pady=10)

pause_button = tk.Button(controls_frame, text="Pause", command=pause_reading, state=tk.DISABLED)
pause_button.pack(side=tk.LEFT, padx=10)

resume_button = tk.Button(controls_frame, text="Resume", command=resume_reading_thread, state=tk.DISABLED)
resume_button.pack(side=tk.LEFT, padx=10)

start_button = tk.Button(root, text="Start Reading Aloud", command=start_reading_thread)
start_button.pack(pady=20)

root.mainloop()
