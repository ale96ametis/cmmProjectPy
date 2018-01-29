# import the necessary packages
from tkinter import *
import numpy as np
from imutils.video import VideoStream
#from imutils import VideoStream
from imutils import face_utils
import datetime
import imutils
import time
import dlib
import cv2
import threading
from PIL import Image, ImageTk

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
	while True:
		# grab the frame from the threaded video stream, resize it to
		# have a maximum width of 400 pixels, and convert it to
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
		img = Image.fromarray(frame)
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

def stop_():
	global stop
	stop = True

def play():
	t = threading.Thread(target=recording)
	t.start()


win = Tk()

win.geometry("800x600")
win.title("Recording app")
stop = False

Label(text='Press Play Button').pack()
frm_ = Frame(bg='black')
frm_.pack()
lbl = Label(frm_, bg='black')
lbl.pack(expand=True)
#lbl.bind('<Double-Button-1>', size)

frm = Frame()
frm.pack()
Button(text='Play', command = play).pack(side=LEFT)
Button(text='Stop', command = stop_).pack(side=LEFT)

win.mainloop()

