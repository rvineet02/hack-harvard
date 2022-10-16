import keyboard
import sounddevice as sd
from scipy.io.wavfile import write
from runner import AssemblyAI

# function to listen for keyboard press events, when down arrow is pressed,
# audio should be recorded for 5 seconds and and writes to file
def on_press(key):
		global recording
		if key == keyboard.KEY_DOWN:
			print("Recording Audio...")
			recording = True
			print("Recording...")
			record_audio()
			print("Done recording")

def record_audio():
	# record audio for 5 seconds
	fs = 44100  # Sample rate
	seconds = 5  # Duration of recording

	myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
	sd.wait()  # Wait until recording is finished
	write('./data/output.wav', fs, myrecording)  # Save as WAV file 

if __name__ == "__main__":
		recording = False
		on_press(keyboard.KEY_DOWN)
		# transcribe audio
		file = "./data/output.wav"
		ai = AssemblyAI()
		transcript = ai.get_transcript(file)
		print(transcript)
