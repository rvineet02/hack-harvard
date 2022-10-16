import cv2
import mediapipe as mp

class Webcam:
    def __init__(self) -> None:
        self.CAMERA = cv2.VideoCapture(0)

    def __landmarks_to_points(self, landmarks, multihands):
        """
        Helper function to convert landmarks to points

        Args:
            landmarks (List[mediapipe.framework.formats.landmark_pb2.NormalizedLandmark]): The landmarks
            multihands (List[mediapipe.framework.formats.classification_pb2.ClassificationList]): The multihands

        Returns:
            Tuple[List[List[Point]], List[Hand]]: The points and hands
        """

        points, hands = [], []
        if landmarks:
            for idx, landmark in enumerate(landmarks):
                points.append([])
                for point in landmark.landmark:
                    points[idx].append((point.x, point.y, point.z))
                hands.append(multihands[idx].classification[0].label)
        return points, hands

    def display_text(self, txt, frame):
        cv2.putText(
            frame,
            txt,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2,
            cv2.LINE_AA
        )

    def process_next(self):
        """
        Helper function to capture points from camera

        Returns:
            Tuple[List[List[Point]], List[Hand]]: The points and hands
        """

        # Load mediapipe
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        mp_hands = mp.solutions.hands

        # Capture webcam
        _, frame = self.CAMERA.read()

        # Flip frame and recolor
        frame = cv2.flip(frame, 1)

        # Convert to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process frame
        with mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=2,
            min_detection_confidence=0.5
        ) as hands:
            frame.flags.writeable = False
            results = hands.process(frame)
            frame.flags.writeable = True

        # Draw landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style(),
                )

        # Store frame for display
        self.last_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Analyze frame
        points, hands = self.__landmarks_to_points(
            results.multi_hand_landmarks,
            results.multi_handedness
        )

        return points, hands, frame