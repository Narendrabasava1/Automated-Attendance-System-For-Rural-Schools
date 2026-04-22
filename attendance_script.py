import cv2
import face_recognition
import os
import numpy as np
from datetime import datetime

path = 'faces'
images = []
classNames = []
encodeListKnown = []

# 🔹 Load images
def load_images():
    global images, classNames
    images = []
    classNames = []

    if not os.path.exists(path):
        os.makedirs(path)

    myList = os.listdir(path)
    for cl in myList:
        img = cv2.imread(f'{path}/{cl}')
        if img is not None:
            images.append(img)
            classNames.append(os.path.splitext(cl)[0])

# 🔹 Encode faces
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodes = face_recognition.face_encodings(img)
        if len(encodes) > 0:
            encodeList.append(encodes[0])
    return encodeList

# Initial load
load_images()
encodeListKnown = findEncodings(images)

# 🔥 Register face
def register_face(name):
    cap = cv2.VideoCapture(0)
    print("Press 's' to capture")

    while True:
        ret, frame = cap.read()
        cv2.imshow("Register Face", frame)

        if cv2.waitKey(1) & 0xFF == ord('s'):
            cv2.imwrite(f'faces/{name}.jpg', frame)
            break

    cap.release()
    cv2.destroyAllWindows()

# 🔥 Reload encodings
def reload_encodings():
    global encodeListKnown
    load_images()
    encodeListKnown = findEncodings(images)

# 🔹 Mark attendance
def mark_attendance(frame, subject):
    imgS = cv2.resize(frame, (0,0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faces = face_recognition.face_locations(imgS)
    encodes = face_recognition.face_encodings(imgS, faces)

    for encodeFace, faceLoc in zip(encodes, faces):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

        if len(faceDis) == 0:
            continue

        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()

            y1,x2,y2,x1 = faceLoc
            y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4

            cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.putText(frame,name,(x1,y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,0.9,(0,255,0),2)

            # Create folder
            if not os.path.exists('Attendance'):
                os.makedirs('Attendance')

            file_name = f'Attendance/{subject}.csv'

            # Create file
            if not os.path.exists(file_name):
                with open(file_name, 'w') as f:
                    f.write("Name,Time\n")

            # Prevent duplicates
            with open(file_name, 'r+') as f:
                data = f.readlines()
                nameList = [line.split(',')[0] for line in data]

                if name not in nameList:
                    now = datetime.now()
                    dt = now.strftime('%H:%M:%S')
                    f.write(f'{name},{dt}\n')

    return frame

# 🔥 Live streaming generator
def generate_frames(subject):
    cap = cv2.VideoCapture(0)

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = mark_attendance(frame, subject)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')