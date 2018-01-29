# import the necessary packages
from tkinter import *
from PIL import Image, ImageTk
from imutils.video import VideoStream
from imutils import face_utils
import datetime
import imutils
import time
import dlib
import cv2
import threading
import numpy as np
import os, sys

def recording():
	# initialize dlib's face detector (HOG-based) and then create
	# the facial landmark predictor
	print("[INFO] loading facial landmark predictor...")
	detector = dlib.get_frontal_face_detector()
	predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

	# initialize the video stream and allow the camera sensor to warmup
	print("[INFO] camera sensor warming up...")
	vs = VideoStream(0).start()
	time.sleep(2.0)
	fourcc = cv2.VideoWriter_fourcc(*'XVID')
	out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640,480))
	# loop over the frames from the video stream
	while stop == False:
		# grab the frame from the threaded video stream, resize it to
		# have a maximum width of 640 pixels, and convert it to
		# grayscale
		frame = vs.read()
		frame = imutils.resize(frame, width=640)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		# detect faces in the grayscale frame
		faces = detector(gray, 0)

		# loop over the face detections
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
		  
		# show the frame
		frame = cv2.flip(frame,1)

		# Put it in the display window
		img = Image.fromarray(frame, mode='RGB')
		img = img.resize((400,400))
		imgtk = ImageTk.PhotoImage(img)
		lbl.config(image=imgtk)
		lbl.img = imgtk
	
		#Save frame for video		
		out.write(frame)
	
		key = cv2.waitKey(1) & 0xFF
	 
		# if the `q` key was pressed, break from the loop
		if key == ord("q") or stop == True:
			print("[INFO] Stopping video and saving file...")
			#Stop recording			
			vs.stop()
			out.release()
			break
	vs.stop()
	out.release()
	return

def stop_():
	global stop
	stop = True
	

def play():
	global stop
	stop = False
	t = threading.Thread(target=recording)
	t.start()

#Initialize Tkinter
win = Tk()
#Reading file with phrases
f = open("frasi.txt","r")
myList = []
for line in f:
	myList.append(line)
n = 7
phrase = myList[n]
#Windows
win.geometry("800x600")
win.title("Recording app")
#Frame
frm = Frame(win)
frm.pack(expand=True)
print("[TESTO]: ", phrase)
stop = None
#Label video
tmp_img = ImageTk.PhotoImage(Image.new('RGB',(400,400)))

lbl = Label(frm)
lbl.config(image=tmp_img)
lbl.img = tmp_img
lbl.grid(row=1, column=1,rowspan=2)
#Label text
text = Label(frm, text=phrase, wraplength=200, justify='center')
text.grid(row=1, column=2, columnspan=4,rowspan=2)
#Buttons
Button(frm, text='Play', command = play).grid(row=2, column=3)
Button(frm, text='Stop', command = stop_).grid(row=2, column=4)

win.mainloop()

