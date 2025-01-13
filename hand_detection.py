import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def initialize_hands():
    return mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

def is_finger_bent(hand_landmarks, finger_mcp, finger_pip, finger_tip, is_thumb=False):
    """
    Determine if a finger is bent.
    Returns True if the finger is bent, otherwise False.
    """
    pip = hand_landmarks.landmark[finger_pip]
    tip = hand_landmarks.landmark[finger_tip]
    if is_thumb:
        # check if the thumb is bent inward (toward the palm)
        mcp = hand_landmarks.landmark[finger_mcp]
        return tip.x < mcp.x if mcp.x < pip.x else tip.x > mcp.x
    else:
        # default logic for other fingers
        return tip.y > pip.y

def get_bent_fingers(hand_landmarks, hand_label):
    """
    Get a list of bent fingers for a single hand.
    """
    fingers = []
    if is_finger_bent(hand_landmarks, mp_hands.HandLandmark.THUMB_CMC,
                      mp_hands.HandLandmark.THUMB_IP,
                      mp_hands.HandLandmark.THUMB_TIP, is_thumb=True):
        fingers.append(4 if hand_label == "Left" else 5)
    if is_finger_bent(hand_landmarks, mp_hands.HandLandmark.INDEX_FINGER_MCP,
                      mp_hands.HandLandmark.INDEX_FINGER_PIP,
                      mp_hands.HandLandmark.INDEX_FINGER_TIP):
        fingers.append(3 if hand_label == "Left" else 6)
    if is_finger_bent(hand_landmarks, mp_hands.HandLandmark.MIDDLE_FINGER_MCP,
                      mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
                      mp_hands.HandLandmark.MIDDLE_FINGER_TIP):
        fingers.append(2 if hand_label == "Left" else 7)
    if is_finger_bent(hand_landmarks, mp_hands.HandLandmark.RING_FINGER_MCP,
                      mp_hands.HandLandmark.RING_FINGER_PIP,
                      mp_hands.HandLandmark.RING_FINGER_TIP):
        fingers.append(1 if hand_label == "Left" else 8)
    if is_finger_bent(hand_landmarks, mp_hands.HandLandmark.PINKY_MCP,
                      mp_hands.HandLandmark.PINKY_PIP,
                      mp_hands.HandLandmark.PINKY_TIP):
        fingers.append(0 if hand_label == "Left" else 9)
    return fingers
