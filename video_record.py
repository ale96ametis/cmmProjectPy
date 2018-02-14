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
			cv2.destroyAllWindows()
		else:
			pass


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
		pass

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
	global ntrial
	global name_video
	print("Stopping recording")
	#audio_thread.stop()
	video_thread.stop()
	landmarks()
	#muxing()
	file_manager()
	ntrial = ntrial+1
	name_video = 'output_phrase[%d]_[%d].avi' %(num_phrase, ntrial)
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
			marker='marker[%d]_[%d].txt' %(num_phrase, ntrial)
			out_file = open(marker,"a")
			for face in faces:
				# determine the facial landmarks for the face region, then
				# convert the facial landmark (x, y)-coordinates to a NumPy
				# array
				shape = predictor(gray, face)
				shape = face_utils.shape_to_np(shape)

				# loop over the (x, y)-coordinates for the facial landmarks
				# and draw them on the image
				mouth_marker = 0
				for (x, y) in shape:
					if (mouth_marker>47):
						cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)
						out_file.write(str(x))
						out_file.write("\n")
						out_file.write(str(y))
						out_file.write("\n")
					mouth_marker += 1
				out_file.write("1000\n")
			out_file.close() 
			frame = cv2.resize(frame, (640,480))
			#cv2.imshow('frame',frame)
			out.write(frame)
			cv2.waitKey(1)
		else:
			out.release()
			cap.release()
			#cv2.destroyAllWindows()
			break
	analyse_marker(marker)
	print('[INFO]End!')
	return


# Required and wanted processing of final files
def file_manager():
	time.sleep(2)
	local_path = os.getcwd()
	str_video = str(name_video)
	if os.path.exists(str(local_path) + "/temp_audio.wav"):
		os.remove(str(local_path) + "/temp_audio.wav")
	#if os.path.exists(str(local_path) + "/" + str_video):
		#os.remove(str(local_path) + "/" + str_video)

	if os.path.exists(str(local_path) + "/temp_video2.avi"):
		os.remove(str(local_path) + "/temp_video2.avi")

	#if os.path.exists(str(local_path) + "/marker-"+str_video):
	#	os.remove(str(local_path) + "/marker-"+name_video)

	
def analyse_marker(current_marker):
	import numpy as np
	base_marker = "base_marker/marker[%d].txt" %(num_phrase)
	f1 = open(base_marker,"r")
	f2 = open(current_marker,"r")

	#global testo1
	#global testo2

	n=100 #righe matrice
	m=40 #colonne matrice

	array1 = np.zeros((n,m)) #matrice per l'inserimento dei valori da file
	array2 = np.zeros((n,m)) #matrice per l'inserimento dei valori da file

	i=0 #indice per scorrere le righe della matrice
	j=0 #indice per scorrere le colonne della matrice e degli array di controllo
	k=0 #indice per scorrere le righe della matrice nell'inserimento dei dati negli array di controllo
	z=0 #indice per scorrere le righe dell'array di controllo

	c=1 #indica quale blocco di "l" righe considerare, quindi se le prime 5 righe, le seconde cinque e via cosi, viene incrementato nel codice
	l=5 #numero di righe da confrontare per fare la media dei valori
	conta=0 #conta quanti valori vengono inseriti in media_tot
	media_tot=0

	check1 = np.zeros((int(n/l),m)) #array di controllo per il calcolo delle medie
	check2 = np.zeros((int(n/l),m)) #array di controllo per il calcolo delle medie
	ris = np.zeros((int(n/l),m)) #array contentente la sottrazione tra le medie calcolate

	while 1:
		
		#leggo il contenuto dei file marker, esco se uno dei due file e' finito
		testo1 = f1.readline()
		if testo1 == "":
			break
		testo2 = f2.readline()
		if testo2 == "":		
			break
			
		#se raggiungo il carattere di controllo sono arrivato a "fine riga" dei marker
		if int(testo1) == 1000: #testo=1000 = carattere di controllo che indice il fine riga dei marker
			#passo alla riga successiva
			i = i+1
			#esco se sforo le dimensioni della matrice (posso ignorare gli ultimi marker)
			if i == n:
				break
				
			#se sono arrivato a fine riga marker riporto a zero la colonna della matrice -> j=0
			j=0
			#leggo i nuovi marker (quelli subito dopo il carattere di controllo)
			testo1 = f1.readline()
			
			#condizioni di uscita
			if testo1 == "":
				break
			testo2 = f2.readline()
			if testo2 == "":		
				break
		
		#salvo il contenuto dei file nelle matrici		
		array1[i][j]=(int(testo1))
		array2[i][j]=(int(testo2))
		
		if i == c*l:	
			while k<i:
				while j<m:
					#inserisco all'interno degli array di check la somma dei valori considerati
					check1[z][j]=check1[z][j]+array1[k][j]
					check2[z][j]=check2[z][j]+array2[k][j]
					j=j+1
				k=k+1
				j=0
				
			while j<m:
				if check1[z][j]==0:
					break
				#calcolo la media degli array di check
				check1[z][j]=check1[z][j]/l
				check2[z][j]=check2[z][j]/l
				ris[z][j]=check1[z][j]-check2[z][j] #array con le medie dei diversi valori
				media_tot=media_tot+abs(ris[z][j]) #media complessiva dell'array ris
				conta=conta+1 #conta quanti valori sono stati inseriti in media_tot
				j=j+1
			z=z+1	
			#riporto j a 0, verra' subito incrementata a 1 ma questo e' ok perche' ho gia' salvato array[i][0] (vedi sopra)
			j=0
			#incremento il controllo sulle righe da considerare
			c=c+1	
		j=j+1
		
	media_tot=media_tot/conta

	#print (array1)
	#print (array2)
	#print (check1)
	#print (check2)
	#print (ris)
	print ("media tot:",media_tot)

	if media_tot < 5:
		print ("lettura corretta")
		result['text'] = "lettura corretta"
	if media_tot > 5 and media_tot < 10:
		print ("lettura con possibilità di qualche piccolo errore")
		result['text'] = "lettura con possibilità di qualche piccolo errore"
	if media_tot > 10 and media_tot < 15:
		print ("lettura con probabile presenza di errori")
		result['text'] = "lettura con probabile presenza di errori"
	if media_tot > 15:
		print ("lettura contenente evidenti errori")
		result['text'] = "lettura contenente evidenti errori"

	f1.close()
	f2.close()



if __name__== "__main__":

	#Initialize Tkinter
	win = Tk()
	#Reading file with phrases
	f = open("frasi.txt","r")
	myList = []
	for line in f:
		myList.append(line)
	global num_phrase
	#num_phrase = randint(0,(len(myList)-1))
	num_phrase = 3
	global ntrial
	ntrial = 0
	phrase = myList[num_phrase]
	global name_video
	name_video ='output_phrase[%d]_[%d].avi' %(num_phrase, ntrial)
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
	lbl.grid(row=1, column=1,rowspan=3)
	#Label text
	text = Label(frm, text=phrase, wraplength=200, justify='center')
	text.grid(row=1, column=2, columnspan=4,rowspan=2)
	#Label text
	result = Label(frm, text="Leggi la frase", justify='center')
	result.grid(row=3, column=2)
	#Buttons
	Button(frm, text='Play', command = start_AVrecording).grid(row=2, column=3)
	Button(frm, text='Stop', command = stop_AVrecording).grid(row=2, column=4)

	win.mainloop()
