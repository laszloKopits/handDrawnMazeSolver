import cv2
import numpy as np
import mazeSolve
import sys

print(sys.argv)

if len(sys.argv) > 1:
    mazeSolve.solve(cv2.imread(sys.argv[1]))
else:
    cap = cv2.VideoCapture(0)

    while(True):
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        cv2.imshow('frame', frame)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('s'):
            mazeSolve.solve(frame)
    cap.release()
    cv2.destroyAllWindows()
