"""
Script used to create a dataset of hand positions
"""

import mediapipe as mp
import cv2
import time
import json
from utils import landmarks_to_tensor

# Mediapipe imports
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

video = cv2.VideoCapture(0)

def save_points(data, label, fname):
    """
    Save data points to json file with label

    Args:
        data (list): List of data points
        label (str): Label of data points
    """
    file = f'./data/raw/{fname}'

    with open(file, 'r') as f:
        prev = json.load(f)

    for d in data:
        prev.append({
            "data": d.tolist(),
            "label": label
        })

    with open(file, 'w') as f:
        json.dump(prev, f)

def harvest(label: str, num_hands: int, num_frames: int, fname: str):
    """
    Runs the harvest script to collect num_frames of data
    for the given label and number of hands

    Args:
        label (str): Label of data points
        num_hands (int): Number of hands to track
    """
    with mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=2,
        min_detection_confidence=0.5
    ) as hands:

        now = time.time()
        
        # For each frame save location
        data_points = []

        while True:
            # Capture webcam frame
            _, frame = video.read()
            
            # Flip frame and recolor
            frame = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process frame
            frame.flags.writeable = False
            results = hands.process(frame)
            frame.flags.writeable = True

            # Recolor frame
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Draw landmarks
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style()
                    )

            # Display countdown (5 seconds to get ready)
            curr_time = time.time()
            time_left = int(5 - (curr_time - now))
            if time_left > 0:
                # Display countdown
                cv2.putText(frame, str(time_left), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), 3, cv2.LINE_AA)
            elif len(data_points) < num_frames: # Save only hand positions in new image
                # Display remaining frames
                remaining_frames_text = f'Remaining frames: {num_frames - len(data_points)}'
                cv2.putText(frame, str(remaining_frames_text), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 2)

                # Extract landmarks and multi hands
                lms = results.multi_hand_landmarks
                multi_hand = results.multi_handedness

                # Convert to tensor
                data, num_detected_hands = landmarks_to_tensor(lms, multi_hand)

                # Store if hand detected
                if num_detected_hands == num_hands:
                    data_points.append(data)
                    print(len(data_points))
            else:
                save_points(data_points, label, fname)
                break
                    
            cv2.imshow("Hand Tracking", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return True

if __name__ == "__main__":
    labels = []
    frames_per_label = 200

    fname = input("Enter filename: ")

    while True:
        label = input("Enter label (or exit): ")

        if label == "exit":
            break

        labels.append(label)
        num_hands = int(input("Enter number of hands: "))
        exited = harvest(label, num_hands, frames_per_label, fname)

        if exited:
            break

    print(f"Saved {len(labels)} labels: {labels}")