from distutils.command.clean import clean
import itertools
import os
import torch
import requests
from dotenv import load_dotenv
load_dotenv()

def normalize_hand(points):
    """
    Normalize the hand points' x, y, and z to be in the range [-1, 1]

    Args:
        points list: List of 3D points (x, y, z)
    """
    # Normalize x
    x_min = torch.min(points[:, 0])
    x_max = torch.max(points[:, 0])
    x_range = x_max - x_min
    points[:, 0] = (points[:, 0] - x_min) / x_range * 2 - 1

    # Normalize y
    y_min = torch.min(points[:, 1])
    y_max = torch.max(points[:, 1])
    y_range = y_max - y_min
    points[:, 1] = (points[:, 1] - y_min) / y_range * 2 - 1

    # Normalize z
    z_min = torch.min(points[:, 2])
    z_max = torch.max(points[:, 2])
    z_range = z_max - z_min
    points[:, 2] = (points[:, 2] - z_min) / z_range * 2 - 1

    # Convert NaNs to 0
    points[torch.isnan(points)] = 0

    return points

def landmarks_to_tensor(lms, multi_hand):
    """
    Convert landmarks to a pytorch tensor

    Args:
        lms (list): List of landmarks
        multi_hand (list): List of handedness

    Returns:
        torch.Tensor: Tensor of shape (42, 3)
    """
    left = right = None

    if lms is None:
        return None, 0

    num_hands = len(lms)

    for idx in range(num_hands):
        landmark = lms[idx]
        hand = multi_hand[idx]

        points_arr = []
        for point in landmark.landmark:
            x = point.x
            y = point.y
            z = point.z
            points_arr.append([x, y, z])

        label = hand.classification[0].label
        if label == "Left":
            left = points_arr
        elif label == "Right":
            right = points_arr

    left_tensor = torch.tensor(left) if left else torch.zeros((21, 3))
    right_tensor = torch.tensor(right) if right else torch.zeros((21, 3))

    left_tensor = normalize_hand(left_tensor)
    right_tensor = normalize_hand(right_tensor)

    data = torch.cat((left_tensor, right_tensor), dim=0)
    return data if left or right else None, num_hands

def consecutive_occurances(ls: list):
    result = []
    for w, c in itertools.groupby(ls):
        result.append((w, len(list(c))))
    return result

def create_sentence(words: list, noise_level: int = 4, separator: str = " ") -> str:
    """
    Create a sentence from a list of words

    Args:
        words (list): List of words

    Returns:
        str: Sentence
    """
    result = consecutive_occurances(words)

    # Remove noise
    result = [[w[0]] * w[1] for w in result if w[1] > noise_level]
    result = [w for w in itertools.chain(*result)]

    # Remove consecutive duplicates
    result = [k for k, _ in consecutive_occurances(result)]
    
    return separator.join(result) or None

cache = {}
def complete_sentence(history: list, text: str) -> str:
    if not text:
        return None
    if text in cache:
        return cache[text]

    input = "Task: convert text a toddler say to a complete sentence\n"
    for msg in history:
        input += msg + "\n"
    input += f"Me: {text}"
    input += "\nToddler meant:"

    url = "https://api.openai.com/v1/completions"
    api_key = os.environ.get("OPENAI_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.post(
        url,
        headers=headers,
        json={
            "prompt": input,
            "model": "text-davinci-002",
            "max_tokens": 50,
            "presence_penalty": 0.5,
            "frequency_penalty": 0.5
        }
    )
    json_res = response.json()
    clean_txt = json_res["choices"][0]["text"].strip()
    
    cache[text] = f"{clean_txt} ({text})"
    return cache[text]

cache_robot = {}
def generate_sentence(history: list) -> str:
    th = tuple(history)
    if th in cache_robot:
        return cache_robot[th]

    input = f"Task: respond as the robot to the conversation between me and a robot that I've met in the middle of a metaverse world in virtual reality"
    for msg in history:
        input += msg + "\n"
    input += "Robot:"

    url = "https://api.openai.com/v1/completions"
    api_key = os.environ.get("OPENAI_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.post(
        url,
        headers=headers,
        json={
            "prompt": input,
            "model": "text-davinci-002",
            "max_tokens": 50,
            "presence_penalty": 0.5,
            "frequency_penalty": 0.5
        }
    )
    json_res = response.json()
    clean_text = json_res["choices"][0]["text"].strip().split("\n")[0].strip()
    cache_robot[th] = f"Robot: {clean_text}"
    return cache_robot[th]