from tkinter import *
from tkinter import ttk
import csv
import random
import os
import glob

BACKGROUND_COLOR = "#B1DDC6"
current_card = {}
learn = []
random_enabled = True
current_index = 0
cards_list = []
MAX_LINE_LENGTH = 20

front_header = "Front"
back_header = "Back"

# ---- CSV helpers ----
def list_csv_files(folder="."):
    # Lists *.csv in the folder (you can change folder to "data" etc.)
    files = glob.glob(os.path.join(folder, "*.csv"))
    # Return just file names (not full paths) for a clean dropdown
    return sorted([os.path.basename(f) for f in files])

def read_csv(filename):
    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            data = list(reader)
            if data and reader.fieldnames and len(reader.fieldnames) >= 2:
                global front_header, back_header
                front_header, back_header = reader.fieldnames[:2]
            return data
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return []
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return []

def initialize_cards():
    global cards_list
    cards_list = learn.copy()
    random.shuffle(cards_list)

def wrap_text(text, max_length):
    words = str(text).split()
    wrapped_text = ""
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + (1 if current_line else 0) <= max_length:
            current_line += (" " + word) if current_line else word
        else:
            wrapped_text += current_line + "\n"
            current_line = word

    wrapped_text += current_line
    return wrapped_text

# ---- Flashcard logic ----
def next_card():
    global current_card, current_index, cards_list

    if learn:
        if random_enabled:
            if not cards_list:
                initialize_cards()
            current_card = cards_list.pop()
        else:
            if current_index >= len(learn):
                current_index = 0
            current_card = learn[current_index]
            current_index += 1

        learn_text = wrap_text(current_card.get(front_header, "Key not found"), MAX_LINE_LENGTH)
        canvas.itemconfig(card_title, text=front_header, fill="black")
        canvas.itemconfig(card_word, text=learn_text, fill="black")
        canvas.itemconfig(card_background, image=card_front_img)
    else:
        canvas.itemconfig(card_title, text="No words left", fill="black")
        canvas.itemconfig(card_word, text="", fill="black")
        canvas.itemconfig(card_background, image=card_front_img)

def flip_card():
    if not current_card:
        return

    if canvas.itemcget(card_title, "text") == front_header:
        back_text = wrap_text(current_card.get(back_header, "Key not found"), MAX_LINE_LENGTH)
        canvas.itemconfig(card_title, text=back_header, fill="white")
        canvas.itemconfig(card_word, text=back_text, fill="white")
        canvas.itemconfig(card_background, image=card_back_img)
    else:
        front_text = wrap_text(current_card.get(front_header, "Key not found"), MAX_LINE_LENGTH)
        canvas.itemconfig(card_title, text=front_header, fill="black")
        canvas.itemconfig(card_word, text=front_text, fill="black")
        canvas.itemconfig(card_background, image=card_front_img)

def toggle_random():
    global random_enabled, current_index
    random_enabled = not random_enabled
    current_index = 0

    if random_enabled:
        initialize_cards()
        toggle_button.config(image=random_on_img)
    else:
        toggle_button.config(image=random_off_img)

def load_selected_csv(event=None):
    """Load deck from dropdown selection."""
    global learn, current_index, current_card, cards_list

    filename = selected_csv.get()
    if not filename:
        return

    learn = read_csv(filename)
    current_index = 0
    current_card = {}
    cards_list = []

    if random_enabled:
        initialize_cards()

    next_card()

# ---- UI ----
window = Tk()
window.title("Flash Cards")
window.config(padx=50, pady=50, bg=BACKGROUND_COLOR)

# Dropdown row (top)
csv_label = Label(window, text="Deck:", font=("Arial", 14), bg=BACKGROUND_COLOR)
csv_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

csv_files = list_csv_files(".")
selected_csv = StringVar(value=csv_files[0] if csv_files else "")

csv_dropdown = ttk.Combobox(
    window,
    textvariable=selected_csv,
    values=csv_files,
    state="readonly",
    width=30
)
csv_dropdown.grid(row=0, column=1, sticky="w", pady=(0, 10))
csv_dropdown.bind("<<ComboboxSelected>>", load_selected_csv)

# Canvas row (below dropdown)
canvas = Canvas(width=800, height=600)
card_front_img = PhotoImage(file="card_front.png")
card_back_img = PhotoImage(file="card_back.png")
card_background = canvas.create_image(400, 263, image=card_front_img)
card_title = canvas.create_text(400, 100, text="", font=("Ariel", 40, "italic"))
card_word = canvas.create_text(400, 263, text="", font=("Ariel", 50, "bold"))
canvas.config(bg=BACKGROUND_COLOR, highlightthickness=0)
canvas.grid(row=1, column=0, columnspan=2)

# Buttons
flip_image = PhotoImage(file="flip.png")
flip_button = Button(image=flip_image, highlightthickness=0, command=flip_card)
flip_button.grid(row=2, column=1)

next_image = PhotoImage(file="next.png")
next_button = Button(image=next_image, highlightthickness=0, command=next_card)
next_button.grid(row=2, column=0)

random_on_img = PhotoImage(file="random_on.png")
random_off_img = PhotoImage(file="random_off.png")
toggle_button = Button(image=random_on_img, highlightthickness=0, command=toggle_random)
toggle_button.grid(row=3, column=0, columnspan=2)

flip_label = Label(window, text="Flip", font=("Arial", 18), bg=BACKGROUND_COLOR)
flip_label.grid(row=3, column=1)

next_label = Label(window, text="Next", font=("Arial", 18), bg=BACKGROUND_COLOR)
next_label.grid(row=3, column=0)

# Load first deck at startup (if any CSV exists)
if csv_files:
    load_selected_csv()
else:
    canvas.itemconfig(card_title, text="No CSV files found", fill="black")
    canvas.itemconfig(card_word, text="Put a .csv in this folder.", fill="black")

window.mainloop()
