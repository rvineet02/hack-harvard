import time
import requests
import os
import threading

import sounddevice as sd
from scipy.io.wavfile import write
from src.utils import generate_sentence

class AssemblyAI:
    def __init__(self, socket = None):
        self.key = os.environ.get("ASSEMBLYAI_KEY")
        self.header = {
            'authorization': self.key,
            'content-type': 'application/json'
        }
        self.endpoint = "https://api.assemblyai.com/v2"
        self.socket = socket

    def __read_file(self, file, chunk_size=1024):
        with open(file, 'rb') as _file:
            while True:
                data = _file.read(chunk_size)
                if not data:
                    break
                yield data

    def __get_upload_url(self, data):
        response = requests.post(f"{self.endpoint}/upload", data=data, headers=self.header)
        res = response.json()
        return res['upload_url']

    def __send_for_transcription(self, audio_url):
        json = {
            "audio_url": audio_url
        }
        response = requests.post(f"{self.endpoint}/transcript", json=json, headers=self.header)
        # status :: "queued" -> "processing" -> "completed"
        res = response.json()
        # get the id and status of the transcription
        return res['id'], res['status']

    def __check_status(self, id):
        response = requests.get(f"{self.endpoint}/transcript/{id}", headers=self.header)
        res = response.json()
        return res['status']

    def __record_audio(self):
        # record audio for 5 seconds
        fs = 44100  # Sample rate
        seconds = 5  # Duration of recording

        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
        sd.wait()  # Wait until recording is finished
        write('./data/audios/output.wav', fs, myrecording)  # Save as WAV file
        self.log("Recording finished, processing file")

        # Get the transcript
        transcript = self.get_transcript("./data/audios/output.wav")

        self.log("Finished processing file")
        
        # Send the transcript to the metaverse
        if self.socket:
            self.socket.write(f"Guest: {transcript}")

            # Get response from robot
            robot_msg = generate_sentence(self.socket.get_history())
            self.socket.writeDelayed(robot_msg)
        else:
            self.log("Transcript: " + transcript)

    def log(self, msg):
        print(f"[AssemblyAI] {msg}")

    def record_audio(self):
        self.log("Starting recording...")

        # Run the recording in a separate thread
        t = threading.Thread(target=self.__record_audio)
        t.start()

    def __get_paragraphs(self, id):
        # make sure the status is completed
        while True:
            status = self.__check_status(id)
            if status == "completed":
                self.log(f"Status: {status}")
                break
            self.log(f"Status: {status}")
            time.sleep(1.5)

        response = requests.get(f"{self.endpoint}/transcript/{id}/paragraphs", headers=self.header)
        res = response.json()
        paras = []
        for p in res['paragraphs']:
            paras.append(p['text'])
        return paras

    def get_transcript(self, file, chunck_size=1024):
        # get the upload url
        upload_url = self.__get_upload_url(self.__read_file(file, chunck_size))
        # send the file for transcription
        id, _ = self.__send_for_transcription(upload_url)
        # get the paragraphs
        paras = self.__get_paragraphs(id)
        return paras[0]