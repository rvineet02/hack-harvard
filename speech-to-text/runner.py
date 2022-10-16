import time
import requests
import os

from dotenv import load_dotenv
load_dotenv()

class AssemblyAI:
	def __init__(self):
		self.key = os.environ.get("key")
		self.header = {
		'authorization': self.key,
		'content-type': 'application/json'
		}
		self.endpoint = "https://api.assemblyai.com/v2"


	def read_file(self, file, chunk_size=1024):
		with open(file, 'rb') as _file:
			while True:
					data = _file.read(chunk_size)
					if not data:
							break
					yield data

	def get_upload_url(self, data):
		response = requests.post(f"{self.endpoint}/upload", data=data, headers=self.header)
		res = response.json()
		return res['upload_url']


	def send_for_transcription(self, audio_url):
		json = {
			"audio_url": audio_url
		}
		response = requests.post(f"{self.endpoint}/transcript", json=json, headers=self.header)
		# status :: "queued" -> "processing" -> "completed"
		res = response.json()
		# get the id and status of the transcription
		return res['id'], res['status']

	def check_status(self, id):
		response = requests.get(f"{self.endpoint}/transcript/{id}", headers=self.header)
		res = response.json()
		return res['status']

	def get_paragraphs(self, id):
		# make sure the status is completed
		while True:
			status = self.check_status(id)
			if status == "completed":
				print(f"Status: {status}")
				break
			print(f"Status: {status}")
			time.sleep(1.5)

		response = requests.get(f"{self.endpoint}/transcript/{id}/paragraphs", headers=self.header)
		res = response.json()
		print(res)
		paras = []
		for p in res['paragraphs']:
			paras.append(p['text'])
		return paras

	def get_transcript(self, file, chunck_size=1024):
		# get the upload url
		upload_url = self.get_upload_url(self.read_file(file, chunck_size))
		# send the file for transcription
		id, status = self.send_for_transcription(upload_url)
		# get the paragraphs
		paras = self.get_paragraphs(id)
		return paras[0]

if __name__ == "__main__":
	file = "./data/impressive.mp3"
	ai = AssemblyAI()
	string = ai.get_transcript(file)
	print(string)
