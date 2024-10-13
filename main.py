import tkinter as tk
from tkinter import filedialog, messagebox
import pyttsx3
import time
import threading
from utils.pdf_reader import extract_text_from_pdf

# Initialize Text-to-Speech engine
engine = pyttsx3.init()

# Global variables
text = ""  # Stores full PDF text
selected_char_index = 0  # Keeps track of the selected character index to start reading
paused = False  # Keeps track of whether the reading is paused
tts_thread = None  # Thread for the TTS process

def read_aloud():
    """Read the text aloud from the selected position, including punctuation."""
    global selected_char_index, paused

    speed = speed_scale.get()
    words_per_pause = words_per_pause_scale.get()
    pause_duration = pause_duration_scale.get() / 1000  # Convert milliseconds to seconds
    engine.setProperty('rate', speed)

    # Get the text starting from the selected character index
    text_to_read = text[selected_char_index:]
    
    # Replace punctuation marks with words
    text_to_read = replace_punctuation(text_to_read)

    words = text_to_read.split()

    current_word_index = 0
    while current_word_index < len(words):
        if paused:  # Check if we should pause
            break

        chunk = ' '.join(words[current_word_index:current_word_index + words_per_pause])
        engine.say(chunk)
        engine.runAndWait()
        current_word_index += words_per_pause
        time.sleep(pause_duration)

    enable_controls()  # Enable controls when reading is done

def replace_punctuation(text):
    """Replace punctuation with words to make the TTS engine read them."""
    replacements = {
        ".": " full stop",
        ",": " comma",
        "!": " exclamation mark",
        "?": " question mark",
        ":": " colon",
        ";": " semicolon",
        "(": " open parenthesis",
        ")": " close parenthesis",
        "'": " apostrophe"
    }
    
    for punct, word in replacements.items():
        text = text.replace(punct, word)
    
    return text


def start_reading_thread():
    """Start reading aloud in a separate thread."""
    global tts_thread, paused

    if text:
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
        text_area.delete(1.0, tk.END)  # Clear existing text in the widget
        text_area.insert(tk.END, text)  # Insert the full PDF text

def select_text():
    """Select the starting point for reading based on the cursor position in the text widget."""
    global selected_char_index
    try:
        # Get the starting position (index) in the form of "line.column"
        start_pos = text_area.index(tk.SEL_FIRST)

        # Convert the "line.column" to an absolute character index
        selected_char_index = text_area.count("1.0", start_pos)[0]  # Count chars from the start to the selection
        messagebox.showinfo("Text Selection", f"Starting from character index {selected_char_index}")
    except tk.TclError:
        messagebox.showwarning("Selection Error", "Please select the starting point.")

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
root.geometry("600x600")

# File upload section
file_frame = tk.Frame(root)
file_frame.pack(pady=20)
file_label = tk.Label(file_frame, text="No PDF selected")
file_label.pack()
upload_button = tk.Button(file_frame, text="Upload PDF", command=upload_pdf)
upload_button.pack()

# PDF content display (Text Area)
text_frame = tk.Frame(root)
text_frame.pack(pady=10)
text_area = tk.Text(text_frame, wrap='word', height=10, width=50)
text_area.pack()

# Select starting point button
select_button = tk.Button(root, text="Select Starting Point", command=select_text)
select_button.pack(pady=10)

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
pause_duration_scale = tk.Scale(pause_duration_frame, from_=100, to_=10000, orient="horizontal")
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
