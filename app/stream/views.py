from datetime import datetime
import os
from django.shortcuts import render
from django.http import StreamingHttpResponse
import  time
import  numpy as np
import face_recognition
import cv2
from .models import Recognition,Students
from threading import Thread
# from  simple_facerec import  SimpleFacerec
# Create your views here.
Name = []
Name.clear
images = []
className =[]
dayNow = datetime.now().date()
myList = os.listdir('stream/DataTrain')
encodeList = []

for item in myList:
    curentImg = cv2.imread(f"stream/DataTrain/{item}")
    images.append(curentImg)
    className.append(os.path.splitext(item)[0])
def Mahoa(images): 
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    
    return encodeList
encodeListKnow = Mahoa(images)

dataStudent = Students.objects.all()
print(dataStudent)

def kiemtratontai(name):
    result = False
    for namee in Name:
        if (name == namee):
            result = True
            break
    return result



def stream():
    cap = cv2.VideoCapture(0)
    pTime = 0
    while True:
        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime=cTime
        now = datetime.now()
        nowStr = now.strftime("%H:%M:%S")
        if (nowStr == '00:00:00'):
            Name.clear()
        
        ret , frame = cap.read()
        if not ret:
            print("Error: Failed to capture image")
            break

        frameHalf = cv2.resize(frame,dsize=None,fx=0.5,fy=0.5)
        frameS = cv2.cvtColor(frameHalf, cv2.COLOR_BGR2RGB)
        faceCurFrame = face_recognition.face_locations(frameS)

        endcodeCurFrame = face_recognition.face_encodings(frameS,faceCurFrame)

        for faceLoc in faceCurFrame:
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 2, x2 * 2, y2 * 2, x1 * 2
            cv2.rectangle(frame, (x1, y1), (x2, y2),(0, 255, 0), 2)


        for encodeFace, faceLoc in zip(endcodeCurFrame,faceCurFrame):
                faceDis = face_recognition.face_distance(encodeListKnow,encodeFace)
                matchIndex = np.argmin(faceDis)
                if faceDis[matchIndex] < 0.45 :
                    maSV = className[matchIndex]
                    print(maSV)
                    kq = kiemtratontai(maSV)
                    if (kq ==False):
                        addStudent = Recognition(time='CURRENT_TIME()',students_id=f'{maSV}')
                        addStudent.save()
                        # std = Students.objects.all(id=f'{maSV}')
                        # print(std)
                        Name.append(maSV)
                        # Name.append(std)
                       
        cv2.putText(frame, f"{now.date()} {nowStr}",(15, 40) , cv2.FONT_ITALIC, 0.5,(0,255,0),1)
        cv2.putText(frame, f"Fps: {int(fps)}",(15, 60) , cv2.FONT_ITALIC, 0.5,(0,255,0),1)
        image_bytes = cv2.imencode('.jpg', frame)[1].tobytes()
        yield(b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + image_bytes + b'\r\n')
def video_feed(request):
    return StreamingHttpResponse(stream(), content_type='multipart/x-mixed-replace; boundary=frame')
def home(request):
    stds = Students.objects.raw("SELECT tbl_students.id,tbl_students.fullName,tbl_students.address,tbl_students.phoneNumber,tbl_recognition.date,tbl_recognition.time AS time FROM `tbl_students`,`tbl_recognition` WHERE tbl_students.id = tbl_recognition.students_id AND tbl_recognition.date='2022-12-21'") 
    return render(request,'index.html',{'stds':stds})