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
		self.end_time = 0

	
	# Video starts being recorded 
	def record(self):
		global recording
		recording = True
#		counter = 1
		timer_start = time.time()
		timer_current = 0
		detector = dlib.get_frontal_face_detector()
		predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
		
		while(self.open==True):
			ret, video_frame = self.video_cap.read()
			if (ret==True):
				
				self.video_out.write(video_frame)
				self.frame_counts += 1

				frame = imutils.resize(video_frame, width=400)
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
				img = Image.fromarray(frame, mode='RGB')
				img = img.resize((500,400))
				imgtk = ImageTk.PhotoImage(img)
				lbl.config(image=imgtk)
				lbl.img = imgtk
				#cv2.imshow('frame',frame)
				"""
				cv2.imshow('video_frame', video_frame)
				cv2.waitKey(1)	
				"""
				time.sleep(0.125)
				# 0.16 delay -> 6 fps
				#
			else:
				break
				

	# Finishes the video recording therefore the thread too
	def stop(self):
		
		if (self.open==True):
			
			self.open=False
			self.end_time = time.time()
			self.video_out.release()
			self.video_cap.release()
			cv2.destroyAllWindows()
		else:
			pass


	# Launches the video recording function using a thread			
	def start(self):
		video_thread = threading.Thread(target=self.record)
		video_thread.start()

def start_AVrecording():
	global video_thread
	if (recording==False):
		video_thread = VideoRecorder()
		video_thread.start()

	return

def stop_AVrecording():
	global ntrial
	global name_video
	global recording
	global nread
	if (recording==True):
		print("Stopping recording")
		video_thread.stop()
		landmarks()
		file_manager()
		ntrial = ntrial+1
		name_video = 'output_phrase[%d]_[%d].avi' %(num_phrase, ntrial)
		print('[INFO]Video saved')
		recording = False
		result['text'] = "Premere Play e leggere una seconda volta per l'analisi"
	if (nread == 1):
		analyse_marker()
		nread = -1
	nread+=1
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
					if (mouth_marker==48):
						x_temp = x
						y_temp = y
					if (mouth_marker>48):
						cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)
						out_file.write(str(x-x_temp))
						out_file.write("\n")
						out_file.write(str(y-y_temp))
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
	print('[INFO]End!')
	return


# Required and wanted processing of final files
def file_manager():
	time.sleep(2)
	local_path = os.getcwd()
	str_video = str(name_video)

	if os.path.exists(str(local_path) + "/temp_video2.avi"):
		os.remove(str(local_path) + "/temp_video2.avi")

	#if os.path.exists(str(local_path) + "/marker-"+str_video):
	#	os.remove(str(local_path) + "/marker-"+name_video)

	
def analyse_marker():
	first_trial = 'marker[%d]_[%d].txt' %(num_phrase, ntrial-2)
	second_trial = 'marker[%d]_[%d].txt' %(num_phrase, ntrial-1)
	f1 = open(first_trial,"r")
	f2 = open(second_trial,"r")

	global testo1
	global testo2

	n=1000 #righe matrice
	m=38 #colonne matrice

	array1 = np.zeros((n,m)) #matrice per l'inserimento dei valori da file
	array2 = np.zeros((n,m)) #matrice per l'inserimento dei valori da file

	i=0 #indice per scorrere le righe della matrice
	j=0 #indice per scorrere le colonne della matrice e degli array di controllo
	k=0 #indice per scorrere le righe della matrice nell'inserimento dei dati negli array di controllo
	z=0 #indice per scorrere le righe dell'array di controllo

	c=1 #indica quale blocco di "l" righe considerare, quindi se le prime 5 righe, le seconde cinque e via cosi, viene incrementato nel codice
	l=10 #numero di facce da confrontare per fare la media dei valori
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
			#passo alla riga successiva e riporto a zero la colonna della matrice -> j=0
			i = i+1
			j = -1
			#esco se sforo le dimensioni della matrice (posso ignorare gli ultimi marker)
			if i == n:
				break

		if int(testo1) != 1000:
			#salvo il contenuto dei file nelle matrici		
			array1[i][j]=(int(testo1))
			array2[i][j]=(int(testo2))
			
		j = j+1

	j=0
	while k<i:
		while j<m:
			#inserisco all'interno degli array di check la somma dei valori considerati
			check1[z][j]=check1[z][j]+array1[k][j]
			check2[z][j]=check2[z][j]+array2[k][j]
			j=j+1
		k=k+1
		c=c+1
		j=0
		if c == l:
			z = z+1
			c=1

	j=0
	z=0
	while z<i:
		while j<m:
			#calcolo la media degli array di check
			check1[z][j]=check1[z][j]/l
			check2[z][j]=check2[z][j]/l
			ris[z][j]=check1[z][j]-check2[z][j]
			media_tot=media_tot+abs(ris[z][j]) #media complessiva dell'array ris
			j=j+1
		z=z+1
		j=0

	index = np.where(~ris.any(axis=1))[0]
	new_ris = np.delete(ris, index, axis=0)

	media_tot=media_tot/(len(new_ris)*n)

	print ("media tot:",media_tot)
	
	if media_tot < 0.05:
		print ("lettura corretta")
		result['text'] = "lettura corretta"
	else:
		print ("lettura contenente errori")
		result['text'] = "lettura contenente errori"

	f1.close()
	f2.close()



if __name__== "__main__":
	global recording
	global num_phrase
	global name_video
	global ntrial
	global nread

	nread=0
	recording = False
	#num_phrase = randint(0,(len(myList)-1))
	num_phrase = 3
	ntrial = 0

	#Reading file with phrases
	f = open("frasi.txt","r")
	myList = []
	for line in f:
		myList.append(line)

	phrase = myList[num_phrase]
	name_video ='output_phrase[%d]_[%d].avi' %(num_phrase, ntrial)
	
	#Initialize Tkinter
	win = Tk()
	
	print("[INFO]Video name: ", name_video)
	print("[TESTO]: ", phrase)
	
	#Windows
	win.geometry("800x600")
	win.title("Recording app")
	
	#Frame
	frm = Frame(win)
	frm.pack(expand=True)

	#Label text
	result = Label(frm, text="Premere Play e leggere la frase. Ripetere la lettura per l'analisi dei marker", justify='center')
	result.grid(row=1, column=1, columnspan=3)
	#Label video
	tmp_img = ImageTk.PhotoImage(Image.new('RGB',(500,400)))
	lbl = Label(frm)
	lbl.config(image=tmp_img)
	lbl.img = tmp_img
	lbl.grid(row=2, column=1,rowspan=3)
	#Label text
	text = Label(frm, text=phrase, wraplength=200, justify='center')
	text.grid(row=2, column=2, columnspan=4,rowspan=2)
	#Buttons
	Button(frm, text='Play', command = start_AVrecording).grid(row=3, column=3)
	Button(frm, text='Stop', command = stop_AVrecording).grid(row=3, column=4)

	win.mainloop()
