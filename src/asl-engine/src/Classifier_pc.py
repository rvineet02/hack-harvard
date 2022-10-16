import pickle
import torch
import cv2
from typing import Literal, Tuple

from src.utils import normalize_hand, create_sentence
from pointnet.PointNet import PointNet, eval_model

from src.AssemblyAI import AssemblyAI
from src.Webcam import Webcam

class Classifier:
    def __init__(self, model: Literal["abc", "conversation"] = "conversation", noise_lvl : int = 4) -> None:
        # Config constants
        self.DEVICE = "mps"
        self.CONFIDENCE_SCORE = 50 # Percent
        self.NOISE_LEVEL = noise_lvl # Number of frames considered noise
        self.MODE = model
        self.assembly_ai = AssemblyAI()

        self.WEBCAM = Webcam()
        with open(f"./model/{model}_id2label.pkl", "rb") as f:
            self.id2label = pickle.load(f)
        self.model = PointNet(classes=len(self.id2label), device=self.DEVICE)
        self.model.load_from_pth(f"./model/{model}.pth")

    def classify_snapshot(self, tensor: torch.Tensor) -> Tuple[str, float]:
        """
        Classifies a single frame of data

        Args:
            tensor (torch.Tensor): The tensor representing the hands

        Returns:
            Tuple[str, float]: The label and confidence score
        """

        predicted_label, score = eval_model(
            self.model,
            tensor,
            self.id2label,
            device=self.DEVICE
        )

        if score < self.CONFIDENCE_SCORE:
            return None, 1
        return predicted_label, score

    def points_to_tensor(self, points, hands) -> torch.Tensor:
        """
        Converts the points to a tensor

        Args:
            points (List[List[Point]]): The points
            hands (List[Hand]): The hands

        Returns:
            torch.Tensor: The tensor
        """
        left = right = None

        num_hands = len(hands)
        for idx in range(num_hands):
            points_arr = points[idx]
            hand = hands[idx]

            if hand == "Left":
                left = points_arr
            elif hand == "Right":
                right = points_arr

        left_tensor = torch.tensor(left) if left else torch.zeros((21, 3))
        right_tensor = torch.tensor(right) if right else torch.zeros((21, 3))

        left_tensor = normalize_hand(left_tensor)
        right_tensor = normalize_hand(right_tensor)

        data = torch.cat((left_tensor, right_tensor), dim=0).to(self.DEVICE)
        return data if (left or right) else None

    def capture_points(self):
        """
        Captures the points from webcam or socket and returns them

        Returns:
            points, hands (Tuple[List[List[Point]], List[Hand]]): The points and hands
        """

        return self.WEBCAM.process_next()

    def display_results(self, text: str, frame):
        """
        Displays the results of the classifier
            
        Args:
            sentences (list): The sentences obtained till now
        """
        # Get text to display
        text = f"Live sentence: {text}" if text else "Live sentence: None"
        self.WEBCAM.display_text(text, frame)

    def log(self, msg: str):
        print(f"[Classifier] {msg}")

    def run(self):
        """
        Main entry point for the classifier
        """
        # For sentence creation (instead of individual words)
        sentences, curr_sentence, curr_nones = [], [], 0

        # For abc only

        self.log("Starting live classification...")
        pred_text = "None"

        while True:
            # Capture points from camera or socket
            points, hands, frame = self.capture_points()

            # Transform data into tensor
            if hands:
                tensor = self.points_to_tensor(points, hands)

                # Classify
                predicted_label, score = self.classify_snapshot(tensor)
                pred_text = f"{predicted_label} ({score})%" if predicted_label else "None"

                # Store prediction for live sentence creation
                if predicted_label is not None:
                    curr_nones = 0
                    curr_sentence.append(predicted_label)
            else:
                curr_nones += 1

                # If curr_nones is greater than NOISE_LEVEL, then we have a sentence
                if curr_nones > self.NOISE_LEVEL:
                    created_sentence = create_sentence(
                        curr_sentence,
                        self.NOISE_LEVEL
                    )
                    curr_sentence = []

                    if created_sentence:
                        sentences.append(created_sentence)

            # Display
            text = sentences[-1] if sentences else None
            self.display_results(pred_text, frame)

            # Convert to BGR for display
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            cv2.imshow("Live Classification", frame)

            key = cv2.waitKey(1)
            if key & 0xFF == ord("q"):
                self.CAMERA.release()
                cv2.destroyAllWindows()
                exit()
            elif key & 0xFF == ord("r"):
                self.assembly_ai.record_audio()
