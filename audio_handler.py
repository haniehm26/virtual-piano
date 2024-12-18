import pygame
import time
import threading
import queue

PATH = "PATH/notes"

pygame.mixer.init()

notes = {
    '1': f'{PATH}/C4.wav',  # Thumb (left hand)
    '2': f'{PATH}/D4.wav',  # Index (left hand)
    '3': f'{PATH}/E4.wav',  # Middle (left hand)
    '4': f'{PATH}/F4.wav',  # Ring (left hand)
    '5': f'{PATH}/G4.wav',  # Pinky (left hand)
    # '6': f'{PATH}/A4.wav',  # Thumb (right hand)
    # '7': f'{PATH}/B4.wav',  # Index (right hand)
    # '8': f'{PATH}/C5.wav',  # Middle (right hand)
    # '9': f'{PATH}/D5.wav',  # Ring (right hand)
    # '0': f'{PATH}/E5.wav'   # Pinky (right hand)
}

# Event queue to handle buffered notes
note_queue = queue.Queue()

# Function to play a note
def play_note(note_file):
    sound = pygame.mixer.Sound(note_file)
    sound.play()

# Function to handle the buffered notes
def play_notes_from_queue():
    while True:
        if not note_queue.empty():
            note_file = note_queue.get()
            play_note(note_file)
            # Small delay to simulate real-time note processing
            time.sleep(0.1)

# Start the note playback handler in a separate thread (non-blocking)
threading.Thread(target=play_notes_from_queue, daemon=True).start()

# Simulated real-time input loop
# TODO (It should be replaced with vision module's output)
while True:
    try:
        # Simulated vision system output (replace with actual detection code)
        # `None` means no finger detected; otherwise, it's a number (e.g., '0', '1', ...)
        input_sequence = input("Enter sequence (e.g., '1n1n2n1n') or a single note (e.g., '1'): ")

        # Process the input sequence
        for char in input_sequence:
            if char.isdigit():
                finger = char
                if finger in notes:
                    # Add note to the queue for playback
                    note_queue.put(notes[finger])

        # Small delay to simulate real-time behavior
        # TODO (adjust as needed)
        time.sleep(0.1)

    except KeyboardInterrupt:
        print("Exiting...")
        break
