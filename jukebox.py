
#import RPi.GPIO as GPIO
import time
import pyaudio
import wave
import keyboard
from pydub import AudioSegment
import numpy as np

## FINAL overley with cycle!
#p.get_device_info_by_index(1)

'''
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
'''
'''
if GPIO.input(4) == GPIO.HIGH:
	print("left button was pressed.")

if GPIO.input(13) == GPIO.HIGH:
	print("right button was pressed.")
'''

def keyboard_is_pressed(key):
	pins = {'q': 4, 'w': 5, 'a':6, 'r': 7, 'p': 8}

	#preturn GPIO.input(pins[key]) == GPIO.HIGH

def record(key='a'):

	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	# CHANNELS = 2 1
	# 2 Bytes in 2 Channels -> 4 Bytes per chunk
	RATE = 16000
	#RATE = 16000 44100
	CHUNK = 1024
	RECORD_SECONDS = 5
	WAVE_OUTPUT_FILENAME = key + '.wav'

	audio = pyaudio.PyAudio()

	# start Recording
	stream = audio.open(format=FORMAT, channels=CHANNELS,
						input_device_index=2,
						rate=RATE, input=True,
						frames_per_buffer=CHUNK)
	frames = []

	#for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
	while keyboard.is_pressed(key):
		data = stream.read(CHUNK)
		frames.append(data)

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

def play(key='a'):
	# length of data to read.
	chunk = 1024

	# create an audio object
	p = pyaudio.PyAudio()

	wf = wave.open(key+'.wav', 'rb')

	# open stream based on the wave object which has been input.
	stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
					channels=wf.getnchannels(),
					rate=wf.getframerate(),
					output_device_index=0,
					output=True)

	# read data (based on the chunk size)
	data = wf.readframes(chunk)

	# play stream (looping from beginning of file to the end)
	while data != b'':
		# writing to the stream is what *actually* plays the sound.
		stream.write(data)
		data = wf.readframes(chunk)

	# cleanup stuff.
	stream.close()
	p.terminate()

def play_final():
	# length of data to read.
	chunk = 1024

	# create an audio object
	p = pyaudio.PyAudio()

	wf = wave.open('q.wav', 'rb')
	# open stream based on the wave object which has been input.
	audio_stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
						  channels=wf.getnchannels(),
						  rate=wf.getframerate(),
						  output_device_index=0,
						  output=True)

	keys = ['q', 'w', 'a']
	keys_pressed = {'q': False, 'w': False, 'a': False}
	keys_playing = {'q': False, 'w': False, 'a': False}
	keys_wav_files = {'q': None, 'w': None, 'a': None}

	just_recorded = True
	while True:
		#final_audio = [0] * chunk * 4
		final_audio = np.zeros(chunk * 2, dtype=np.int32)
		for key in keys:

			if keys_playing[key]:
				if keys_wav_files[key] is None:
					wav_file = wave.open(key + '.wav', 'rb')
					keys_wav_files[key] = wav_file

				single_audio = list(keys_wav_files[key].readframes(chunk))
				single_audio = np.array(single_audio, dtype=np.int8).view('<i2')
				if single_audio == b'' or len(single_audio) == 0:
					wav_file = wave.open(key + '.wav', 'rb')
					keys_wav_files[key] = wav_file

					single_audio = list(keys_wav_files[key].readframes(chunk))
					single_audio = np.array(single_audio, dtype=np.int8).view('<i2')

				final_audio = final_audio + single_audio

		num_audios = sum(keys_playing.values())
		if num_audios == 0:
			num_audios = 1

		final_audio = final_audio / num_audios

		final_audio[final_audio >= 2**16 -1] = 2**16-1
		final_audio[final_audio < -2**16] = -2**16

		final_audio = final_audio.astype(np.int16)
		audio_stream.write(bytes(final_audio))

		for key in keys:
			if keyboard.is_pressed(key) and not keys_pressed[key]:
				keys_playing[key] = not keys_playing[key]

			keys_pressed[key] = keyboard.is_pressed(key)

		if not keyboard.is_pressed('p'):
			just_recorded = False
		elif keyboard.is_pressed('p') and not just_recorded:
			audio_stream.close()
			p.terminate()
			return


def mix(keys=['q', 'w', 'a']):
	segments = []
	print('mixing')
	for key in keys:
		segments.append(AudioSegment.from_file(key + '.wav'))

	final = segments[0]
	for i in range(1, len(keys)):
		final = final.overlay(segments[i])

	final.export('final.wav', format='wav')


mode = 'record'
just_played = False

while True:

	print('mode: ', mode)

	if mode == 'record':
		keys = ['q', 'w', 'a']

		for key in keys:
			if keyboard.is_pressed(key):
				if keyboard.is_pressed('r'):
					print('recording ' + key + ' ...')
					record(key)
					print('end of recording '+ key)
				else:
					print('playing ' + key + ' ...')
					play(key)
					print('end of playing ' + key)

		if not keyboard.is_pressed('p'):
			just_played = False

		elif keyboard.is_pressed('p') and not just_played:
			mode = 'play'

	elif mode == 'play':
		print('playing final...')
		play_final()

		print('end of playing final.')
		mode = 'record'
		just_played = True

	time.sleep(0.1)