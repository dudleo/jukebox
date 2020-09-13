import pyaudio
import wave
import keyboard

def record(key='a'):

	FORMAT = pyaudio.paInt16
	CHANNELS = 2
	# 2 Bytes in 2 Channels -> 4 Bytes per chunk
	RATE = 44100
	CHUNK = 1024
	RECORD_SECONDS = 5
	WAVE_OUTPUT_FILENAME = key + '.wav'

	audio = pyaudio.PyAudio()

	# start Recording
	stream = audio.open(format=FORMAT, channels=CHANNELS,
						input_device_index=0,
						rate=RATE, input=True,
						frames_per_buffer=CHUNK)
	print("recording...")
	frames = []

	#for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
	while keyboard.is_pressed(key):
		data = stream.read(CHUNK)
		frames.append(data)
	print("finished recording")

	# stop Recording
	stream.stop_stream()
	stream.close()
	audio.terminate()

	waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	waveFile.setnchannels(CHANNELS)
	waveFile.setsampwidth(audio.get_sample_size(FORMAT))
	waveFile.setframerate(RATE)
	waveFile.writeframes(b''.join(frames))
	waveFile.close()