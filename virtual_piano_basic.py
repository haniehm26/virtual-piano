import time
import cv2 as cv
import numpy as np
from collections import deque

from audio_handler import initialize_midi, note_on, note_off
from metrics import calculate_fps, monitor_cpu_usage, smooth_cpu_usage

from constants import (
    NOTES, KERNEL_SIZE, WINDOW_NAME, RESET_TIME, FLIP,
    KEY_HEIGHT, THRESHOLD, SAVE_CHECK_TIME, NOTE_NAMES, NUM_KEYS,
    COMPARISON_VALUE, CONSTANT_BACKGROUND, RED, BLUE, BLACK
)


def detect_skin(frame):
    """
    Detects skin regions in an input image. It returns a binary mask where the skin
    regions are white (255), and non-skin regions are black (0).
    """
    hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    lower = np.array([0, 48, 80], dtype = "uint8")
    upper = np.array([20, 255, 255], dtype = "uint8")
    skin_mask = cv.inRange(hsv_frame, lower, upper)
    return skin_mask

def compare(a, b):
    return cv.threshold(cv.absdiff(a, b), THRESHOLD, COMPARISON_VALUE, cv.THRESH_BINARY)[1]

midiout = initialize_midi()
is_playing = NUM_KEYS * [False]

video = cv.VideoCapture(0) 

frame_width = int(video.get(cv.CAP_PROP_FRAME_WIDTH))
frame_height = int(video.get(cv.CAP_PROP_FRAME_HEIGHT))

scaled_width = frame_width
scaled_height = frame_height

display_width = frame_width
display_height = frame_height

kernel_size = 2 * int(KERNEL_SIZE * scaled_width / 2) + 1

cv.namedWindow(WINDOW_NAME, cv.WINDOW_AUTOSIZE)
cv.resizeWindow(WINDOW_NAME, display_width, display_height)

display_rects, scaled_rects, frame_rects = [], [], []

for i in range(NUM_KEYS):
    x0 = scaled_width * i // NUM_KEYS
    x1 = scaled_width * (i + 1) // NUM_KEYS - 1
    r = [(x0, 0), (x1, int(KEY_HEIGHT * scaled_height))]
    scaled_rects.append(r)

    x0 = frame_width * i // NUM_KEYS
    x1 = frame_width * (i + 1) // NUM_KEYS - 1
    r = [(x0, 0), (x1, int(KEY_HEIGHT * frame_height))]
    frame_rects.append(r)

    x0 = display_width * i // NUM_KEYS
    x1 = display_width * (i + 1) // NUM_KEYS - 1
    r = [(x0, 0), (x1, int(KEY_HEIGHT * display_height))]
    display_rects.append(r)

keys_top_left_scaled = (min(r[0][0] for r in scaled_rects), min(r[0][1] for r in scaled_rects))
keys_bottom_right_scaled = (max(r[1][0] for r in scaled_rects), max(r[1][1] for r in scaled_rects))
keys_width_scaled = keys_bottom_right_scaled[0] - keys_top_left_scaled[0]
keys_heigh_scaled = keys_bottom_right_scaled[1] - keys_top_left_scaled[1]

keys = np.zeros((keys_heigh_scaled, keys_width_scaled), dtype=np.uint8)

for i in range(NUM_KEYS):
    r = scaled_rects[i]
    cv.rectangle(keys, (r[0][0] - keys_top_left_scaled[0], r[0][1] - keys_top_left_scaled[1]),
                  (r[1][0] - keys_top_left_scaled[0], r[1][1] - keys_top_left_scaled[1]), i + 1, cv.FILLED)

saved_frame = None
comparison_frame = None
saved_time = 0
last_check_time = 0

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

        keys_frame = frame[keys_top_left_scaled[1]:keys_bottom_right_scaled[1], keys_top_left_scaled[0]:keys_bottom_right_scaled[0]]
        if scaled_width != frame_width:
            keys_frame = cv.resize(keys_frame, (keys_width_scaled, keys_heigh_scaled))
        keys_frame = cv.cvtColor(keys_frame, cv.COLOR_BGR2GRAY)

        blurred = cv.GaussianBlur(keys_frame, (kernel_size, kernel_size), 0)

        if CONSTANT_BACKGROUND:
            t = time.time()
            save = False
            if saved_frame is None:
                save = True
                last_check_time = t
            else:
                if t >= last_check_time + SAVE_CHECK_TIME:
                    if COMPARISON_VALUE in compare(saved_frame, blurred):
                        save = True
                    last_check_time = t
                if t >= saved_time + RESET_TIME:
                    comparison_frame = blurred
                    save = True
            if save:
                saved_frame = blurred
                saved_time = t

        if comparison_frame is None:
            comparison_frame = blurred
            continue

        delta = compare(comparison_frame, blurred)
        sum = keys + delta
        cv.imshow("Difference Between Frames", delta)

        valid_frame = False 
        for i in range(NUM_KEYS):
            r = display_rects[i]
            motion_detected = 1 + i + COMPARISON_VALUE in sum
            detected_region = frame[r[0][1]:r[1][1], r[0][0]:r[1][0]]
            
            skin_mask = detect_skin(detected_region)
            skin_pixels = cv.countNonZero(skin_mask)
            total_pixels = skin_mask.size

            skin_detected = skin_pixels > 0.02 * total_pixels

            if motion_detected and skin_detected:
                valid_frame = True
                overlay = frame.copy()
                cv.rectangle(overlay, r[0], r[1], BLUE, cv.FILLED)
                cv.addWeighted(overlay, 0.3, frame, 1 - 0.3, 0, frame)
                if not is_playing[i]:
                    note_on(midiout, NOTES[i])
                    is_playing[i] = True
            else:
                valid_frame = False
                if is_playing[i]:
                    note_off(midiout, NOTES[i])
                    is_playing[i] = False

            cv.rectangle(frame, r[0], r[1], BLACK, 1)
            cv.putText(frame, NOTE_NAMES[i], (r[0][0]+20, r[0][1]+30), cv.FONT_HERSHEY_SIMPLEX, 1, BLACK, 1, cv.LINE_AA)

        frame_count += 1

        fps = calculate_fps(frame_count, start_time)
        cpu_usage, last_cpu_check_time = monitor_cpu_usage(last_cpu_check_time, interval=0.5)
        smoothed_cpu = smooth_cpu_usage(cpu_usage, cpu_history, max_history=10)
        cv.putText(frame, f"fps: {fps:.2f}, cpu_usage: {smoothed_cpu:.2f}", (10, display_height - 10), cv.FONT_HERSHEY_SIMPLEX, 1.1, RED, 3, cv.LINE_AA)

        display = cv.resize(frame, (display_width, display_height)) if frame_width != display_width else frame
        cv.imshow(WINDOW_NAME, cv.addWeighted(display, 1, frame, 0.25, 1.0))
        
        if cv.waitKey(1) & 0xFF == 27:
            break
finally:
    midiout.close_port()
    video.release()
    cv.destroyAllWindows()