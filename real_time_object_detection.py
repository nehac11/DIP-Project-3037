from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2


ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
	help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
	help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
	help="minimum probability to filter weak predictions")
args = vars(ap.parse_args())


CLASSES = ["aeroplane", "background", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

# Assigning random colors to each of the classes
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))


print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
# warm up the camera for a couple of seconds
time.sleep(2.0)


fps = FPS().start()


while True:
	
	frame = vs.read()
	frame = imutils.resize(frame, width=400)
	print(frame.shape) # (225, 400, 3)
	# grab the frame dimensions and convert it to a blob
	# First 2 values are the h and w of the frame. Here h = 225 and w = 400
	(h, w) = frame.shape[:2]
	# Resize each frame
	resized_image = cv2.resize(frame, (300, 300))
	

	blob = cv2.dnn.blobFromImage(resized_image, (1/127.5), (300, 300), 127.5, swapRB=True)
	
	net.setInput(blob) # net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])
	# Predictions:
	predictions = net.forward()

	# loop over the predictions
	for i in np.arange(0, predictions.shape[2]):
		
		confidence = predictions[0, 0, i, 2]
		
		if confidence > args["confidence"]:
			
			idx = int(predictions[0, 0, i, 1])
			# then compute the (x, y)-coordinates of the bounding box for the object
			box = predictions[0, 0, i, 3:7] * np.array([w, h, w, h])
			
			(startX, startY, endX, endY) = box.astype("int")

			# Get the label with the confidence score
			label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
			print("Object detected: ", label)
			# Draw a rectangle across the boundary of the object
			cv2.rectangle(frame, (startX, startY), (endX, endY),
				COLORS[idx], 2)
			y = startY - 15 if startY - 15 > 15 else startY + 15
			# Put a text outside the rectangular detection
			# Choose the font of your choice: FONT_HERSHEY_SIMPLEX, FONT_HERSHEY_PLAIN, FONT_HERSHEY_DUPLEX, FONT_HERSHEY_COMPLEX, FONT_HERSHEY_SCRIPT_COMPLEX, FONT_ITALIC, etc.
			cv2.putText(frame, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

	# show the output frame
	cv2.imshow("Frame", frame)

	

	key = cv2.waitKey(1) & 0xFF

	# Press 'q' key to break the loop
	if key == ord("q"):
		break

	# update the FPS counter
	fps.update()

# stop the timer
fps.stop()

# Display FPS Information: Total Elapsed time and an approximate FPS over the entire video stream
print("[INFO] Elapsed Time: {:.2f}".format(fps.elapsed()))
print("[INFO] Approximate FPS: {:.2f}".format(fps.fps()))

# Destroy windows and cleanup
cv2.destroyAllWindows()
# Stop the video stream
vs.stop()



#python real_time_object_detection.py --prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel