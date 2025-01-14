import cv2 as cv
import time
from collections import deque

from hand_detection import initialize_hands, get_bent_fingers, mp_drawing, mp_hands
from audio_handler import initialize_midi, note_on, note_off
from metrics import calculate_fps, monitor_cpu_usage, smooth_cpu_usage

from constants import NOTES, NOTE_NAMES, BLACK, WHITE, BLUE, RED, NUM_KEYS, WINDOW_NAME, FLIP

def draw_piano_keys(frame, active_keys, key_height=100):
    frame_height, frame_width, _ = frame.shape
    key_width = frame_width // NUM_KEYS

    for i in range(NUM_KEYS):
        x = i * key_width
        y = frame_height - key_height
        color = BLUE if i in active_keys else WHITE
        overlay = frame.copy()
        cv.rectangle(overlay, (x, y), (x + key_width, frame_height), color, cv.FILLED)
        cv.addWeighted(overlay, 0.3, frame, 1 - 0.3, 0, frame)
        cv.rectangle(frame, (x, y), (x + key_width, frame_height), BLACK, 2)
        text_size = cv.getTextSize(NOTE_NAMES[i], cv.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
        text_x = x + (key_width - text_size[0]) // 2
        text_y = y + (key_height + text_size[1]) // 2
        cv.putText(frame, NOTE_NAMES[i], (text_x, text_y), cv.FONT_HERSHEY_SIMPLEX, 0.6, BLACK, 1)


midiout = initialize_midi()
is_playing = [False] * NUM_KEYS

hands = initialize_hands()

video = cv.VideoCapture(0)

# FPS counter
start_time = time.time()
frame_count = 0
last_cpu_check_time = start_time
cpu_history = deque()

try:
    while video.isOpened():
        ok, frame = video.read()
        if not ok:
            print("Failed to read frame.")
            break
        if FLIP:
            frame = cv.flip(frame, 1)

        # process frame with MediaPipe
        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        # get bent fingers
        bent_fingers = []
        if results.multi_hand_landmarks:
            for hand_landmarks, hand_class in zip(results.multi_hand_landmarks, results.multi_handedness):
                hand_label = hand_class.classification[0].label
                bent_fingers.extend(get_bent_fingers(hand_landmarks, hand_label))
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # manage active keys and sound
        active_keys = []
        for finger in bent_fingers:
            if not is_playing[finger]:
                note_on(midiout, NOTES[finger])
                is_playing[finger] = True
            active_keys.append(finger)

        for i, is_pressed in enumerate(is_playing):
            if i not in active_keys and is_pressed:
                note_off(midiout, NOTES[i])
                is_playing[i] = False

        draw_piano_keys(frame, active_keys)

        frame_count += 1

        fps = calculate_fps(frame_count, start_time)
        cpu_usage, last_cpu_check_time = monitor_cpu_usage(last_cpu_check_time, interval=0.5)
        smoothed_cpu = smooth_cpu_usage(cpu_usage, cpu_history, max_history=10)
        cv.putText(frame, f"fps: {fps:.2f}, cpu_usage: {smoothed_cpu:.2f}%", (30, 30), cv.FONT_HERSHEY_SIMPLEX, 1.1, RED, 3, cv.LINE_AA)

        cv.imshow(WINDOW_NAME, frame)

        if cv.waitKey(1) & 0xFF == 27:
            break
finally:
    midiout.close_port()
    video.release()
    cv.destroyAllWindows()