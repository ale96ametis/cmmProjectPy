# import the necessary packages
from tkinter import *
from PIL import Image, ImageTk
from imutils.video import VideoStream
from imutils import face_utils
from random import randint
import datetime
import imutils
import time
import dlib
import cv2
import threading
import numpy as np
import os, sys
import pyaudio
import wave
import subprocess

class VideoRecorder():
	
	# Video class based on openCV 
	def __init__(self):
		
		self.open = True
		self.device_index = 0
		self.fps = 6               # fps should be the minimum constant rate at which the camera can
		self.fourcc = "MJPG"       # capture images (with no decrease in speed over time; testing is required)
		self.frameSize = (640,480) # video formats and sizes also depend and vary according to the camera used
		self.video_filename = name_video
		self.video_cap = cv2.VideoCapture(self.device_index)
		self.video_writer = cv2.VideoWriter_fourcc(*self.fourcc)
		self.video_out = cv2.VideoWriter(self.video_filename, self.video_writer, self.fps, self.frameSize)
		self.frame_counts = 1
		self.start_time = time.time()

	
	# Video starts being recorded 
	def record(self):
		
#		counter = 1
		timer_start = time.time()
		timer_current = 0
		
		
		while(self.open==True):
			ret, video_frame = self.video_cap.read()
			if (ret==True):
				
				self.video_out.write(video_frame)
				self.frame_counts += 1
				time.sleep(0.14)
				
				# Uncomment the following three lines to make the video to be
				# displayed to screen while recording
				img = Image.fromarray(video_frame, mode='RGB')
				img = img.resize((500,400))
				imgtk = ImageTk.PhotoImage(img)
				lbl.config(image=imgtk)
				lbl.img = imgtk
				"""
				cv2.imshow('video_frame', video_frame)
				cv2.waitKey(1)
				"""
				# 0.16 delay -> 6 fps
				#
			else:
				break
				

	# Finishes the video recording therefore the thread too
	def stop(self):
		
		if (self.open==True):
			
			self.open=False
			self.video_out.release()
			self.video_cap.release()
			#cv2.destroyAllWindows()


	# Launches the video recording function using a thread			
	def start(self):
		video_thread = threading.Thread(target=self.record)
		video_thread.start()

class AudioRecorder():
	
	# Audio class based on pyAudio and Wave
	def __init__(self):
		
		self.open = True
		self.rate = 44100
		self.frames_per_buffer = 1024
		self.channels = 2
		self.format = pyaudio.paInt16
		self.audio_filename = "temp_audio.wav"
		self.audio = pyaudio.PyAudio()
		self.stream = self.audio.open(format=self.format,
									  channels=self.channels,
									  rate=self.rate,
									  input=True,
									  frames_per_buffer = self.frames_per_buffer)
		self.audio_frames = []

	# Audio starts being recorded
	def record(self):

		self.stream.start_stream()
		while(self.open == True):
			data=self.stream.read(self.frames_per_buffer)
			self.audio_frames.append(data)
			if (self.open==False):
				break

	# Finishes the audio recording therefore the thread too    
	def stop(self):
		
		if (self.open==True):
			self.open = False
			self.stream.stop_stream()
			self.stream.close()
			self.audio.terminate()

			waveFile = wave.open(self.audio_filename, 'wb')
			waveFile.setnchannels(self.channels)
			waveFile.setsampwidth(self.audio.get_sample_size(self.format))
			waveFile.setframerate(self.rate)
			waveFile.writeframes(b''.join(self.audio_frames))
			waveFile.close()

	# Launches the audio recording function using a thread
	def start(self):
		audio_thread = threading.Thread(target=self.record)
		audio_thread.start()

def start_AVrecording():
	
	global video_thread
	#global audio_thread

	video_thread = VideoRecorder()
	#audio_thread = AudioRecorder()

	#audio_thread.start()
	video_thread.start()

	return

def stop_AVrecording():
	global i
	global name_video
	print("Stopping recording")
	#audio_thread.stop()
	video_thread.stop()
	landmarks()
	#muxing()
	file_manager()
	i = i+1
	name_video = 'output_phrase[%d]_[%d].avi' %(n, i)
	print('[INFO]Video saved')
	return
	
def muxing():
	# Makes sure the threads have finished
	#while threading.active_count() > 1:
	#	time.sleep(1)

	frame_counts = video_thread.frame_counts
	elapsed_time = time.time() - video_thread.start_time
	recorded_fps = frame_counts / elapsed_time
	print("total frames " + str(frame_counts))
	print("elapsed time " + str(elapsed_time))
	print("recorded fps " + str(recorded_fps))
#	 Merging audio and video signal
	
	if abs(recorded_fps - 6) >= 0.01:    # If the fps rate was higher/lower than expected, re-encode it to the expected
								
		print("Re-encoding")
		cmd = "ffmpeg -r " + str(recorded_fps) + " -i marker-"+name_video+" -pix_fmt yuv420p -r 6 temp_video2.avi"
		subprocess.call(cmd, shell=True)

		print("Muxing")
		cmd = "ffmpeg -ac 2 -channel_layout stereo -i temp_audio.wav -i temp_video2.avi -pix_fmt yuv420p " + "complete-"+name_video
		subprocess.call(cmd, shell=True)

	else:

		print("Normal recording\nMuxing")
		cmd = "ffmpeg -ac 2 -channel_layout stereo -i temp_audio.wav -i marker-"+name_video+" -pix_fmt yuv420p " + "complete-"+name_video
		subprocess.call(cmd, shell=True)

		print("..")
	return

	
def landmarks():
	fourcc = cv2.VideoWriter_fourcc(*'MJPG')
	out = cv2.VideoWriter('marker-'+name_video, fourcc, 20.0, (640,480))
	detector = dlib.get_frontal_face_detector()
	predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
	cap = cv2.VideoCapture(name_video)
	print("[INFO]Analysing video...")
	while(cap.isOpened()):
		ret,frame = cap.read()
		if (ret):
			frame = imutils.resize(frame, width=400)
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			faces = detector(gray, 0)
			#loop over the face detections
			for face in faces:
				# determine the facial landmarks for the face region, then
				# convert the facial landmark (x, y)-coordinates to a NumPy
				# array
				shape = predictor(gray, face)
				shape = face_utils.shape_to_np(shape)

				# loop over the (x, y)-coordinates for the facial landmarks
				# and draw them on the image
				for (x, y) in shape:
					cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)
			frame = cv2.resize(frame, (640,480))
			#cv2.imshow('frame',frame)
			out.write(frame)
			cv2.waitKey(1)
		else:
			out.release()
			cap.release()
			#cv2.destroyAllWindows()
			break
	print('[INFO]End!')
	return


# Required and wanted processing of final files
def file_manager():
	time.sleep(2)
	local_path = os.getcwd()
	str_video = str(name_video)
	if os.path.exists(str(local_path) + "/temp_audio.wav"):
		os.remove(str(local_path) + "/temp_audio.wav")
	if os.path.exists(str(local_path) + "/" + str_video):
		os.remove(str(local_path) + "/" + str_video)

	if os.path.exists(str(local_path) + "/temp_video2.avi"):
		os.remove(str(local_path) + "/temp_video2.avi")

	#if os.path.exists(str(local_path) + "/marker-"+str_video):
	#	os.remove(str(local_path) + "/marker-"+name_video)


if __name__== "__main__":

	#Initialize Tkinter
	win = Tk()
	#Reading file with phrases
	f = open("frasi.txt","r")
	myList = []
	for line in f:
		myList.append(line)
	n = randint(0,(len(myList)-1))
	global i
	i = 0
	phrase = myList[n]
	global name_video
	name_video ='output_phrase[%d]_[%d].avi' %(n, i)
	print("[INFO]Video name: ", name_video)
	#Windows
	win.geometry("800x600")
	win.title("Recording app")
	#Frame
	frm = Frame(win)
	frm.pack(expand=True)
	print("[TESTO]: ", phrase)
	#Label video
	tmp_img = ImageTk.PhotoImage(Image.new('RGB',(500,400)))
	lbl = Label(frm)
	lbl.config(image=tmp_img)
	lbl.img = tmp_img
	lbl.grid(row=1, column=1,rowspan=2)
	#Label text
	text = Label(frm, text=phrase, wraplength=200, justify='center')
	text.grid(row=1, column=2, columnspan=4,rowspan=2)
	#Buttons
	Button(frm, text='Play', command = start_AVrecording).grid(row=2, column=3)
	Button(frm, text='Stop', command = stop_AVrecording).grid(row=2, column=4)

	win.mainloop()
