from flask import Flask, render_template, request, flash

from flask import Response
import csv
from keras.models import load_model
import numpy as np
from pygame import mixer
from flask import session
import tensorflow as tf

import sys
import os
import io
import cv2
import smtplib
from email.mime.text import MIMEText

from DBConfig import DBConnection


app = Flask(__name__)
app.secret_key = "abc"


@app.route('/')
def index():
    return render_template('user.html')


@app.route("/user")
def user():
    return render_template("user.html")


@app.route("/drowsy_detection")
def drowsy_detection():
    return render_template("drowsy_detection.html")


@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/forgotpassword")
def forgotpassword():
    return render_template("forgotpassword.html")


@app.route("/newuser")
def newuser():
    return render_template("register.html")

@app.route("/userlogin_check", methods=["GET", "POST"])
def userlogin_check():

    uid = request.form.get("unm")
    pwd = request.form.get("pwd")

    database = DBConnection.getConnection()
    cursor = database.cursor()
    sql = "select count(*) from register where userid='" + \
        uid + "' and passwrd='" + pwd + "'"
    cursor.execute(sql)
    res = cursor.fetchone()[0]
    if res > 0:
        session['uid'] = uid

        return render_template("user_home.html")
    else:

        return render_template("user.html", msg2="Invalid Credentials")

    return ""

@app.route("/user_register", methods=["GET", "POST"])
def user_register():
    try:
        sts = ""
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        gender = request.form.get('gender')
        dob = request.form.get('dob')
        pwd = request.form.get('pwd')
        mno = request.form.get('mno')
        email = request.form.get('email')
        height = request.form.get('height')
        age = request.form.get('age')
        weight = request.form.get('weight')

        database = DBConnection.getConnection()
        cursor = database.cursor()
        sql = "select count(*) from register where email='"+email+"'"

        cursor.execute(sql)
        res = cursor.fetchone()[0]
        if res > 0:
            sts = 0
        else:
            sql = "insert into register values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            values = (firstname, lastname, pwd, email, mno, gender, dob,height,weight,age)
            cursor.execute(sql, values)
            database.commit()
            sts = 1

        if sts == 1:
            return render_template("user.html", msg="Registered Successfully..! Login Here.")

        else:
            return render_template("register.html", msg="User Id with email already exists. Please try to login or reset your password!")

    except Exception as e:
        print(e)

    return ""



@app.route("/resetpwd",methods=["GET", "POST"])
def resetpwd():
    try:
        sts2 = ""
        uid = request.form.get('uid')
        pwd1 = request.form.get('pwd1')
        pwd2 = request.form.get('pwd2')

        database1 = DBConnection.getConnection()
        cursor = database1.cursor()
        sql = "select count(*) from register where userid='" + \
        uid + "' and userid='" + uid + "'"
        cursor.execute(sql)
        res1 = cursor.fetchone()[0]
        if res1 > 0:
            sql = "update register set passwrd = %s where userid = %s"
            values = (pwd2 , uid)
            cursor.execute(sql, values)
            database1.commit()
            sts2 = 1
        else:
            sts2 = 0
        
        if sts2 == 1:
            return render_template("user.html", msg3="Password reset Successfully..! Login Here.")

        else:
         return render_template("user.html", msg4="User Id does not exist..!")

    except Exception as e:
        print(e)

    return ""

@app.route('/sendEmail', methods=["GET", "POST"])
def sendEmail():

   
    s = smtplib.SMTP('smtp.gmail.com:587')
    s.starttls()

    eid = request.form.get('eid')
    sender = 'driverdrowsinessdetection5@gmail.com'
    receivers = [eid]
   
    s.login(sender, "yenzksnucrlgnkap")

    message = """From: ${sender} 
    To: ${receivers}
    Subject: SMTP e-mail test from driver drowsiness detection
    We received your password change request. Please <a href ="http://localhost:1357/ChangePassword">Click here</a> to set a new password.
    """

    msg = MIMEText(message ,'html')
    s.sendmail(sender, receivers, msg.as_string())         
    print("Successfully sent email")

    return render_template("Confirmation.html")



@app.route("/ChangePassword",methods=["GET", "POST"])
def ChangePassword():
    return render_template("ChangePassword.html")


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


def gen_frames():

    try:
        
        count = 0
        score = 0
        thicc = 2
        rpred = [99]
        lpred = [99]
        camera = cv2.VideoCapture(0)
        font = cv2.FONT_HERSHEY_COMPLEX_SMALL
        mixer.init()
        sound = mixer.Sound('DrowsinessDetection/alarm.wav')

        face = cv2.CascadeClassifier(
            'DrowsinessDetection/haarcascade_frontalface_alt.xml')
        leye = cv2.CascadeClassifier(
            'DrowsinessDetection/haarcascade_lefteye_2splits.xml')
        reye = cv2.CascadeClassifier(
            'DrowsinessDetection/haarcascade_righteye_2splits.xml')
        model = load_model('DrowsinessDetection/cnn_eyes.h5')
        while True:
            success, frame = camera.read()  # read the camera frame
            height, width = frame.shape[:2]
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face.detectMultiScale(
                gray, minNeighbors=5, scaleFactor=1.1, minSize=(25, 25))
            left_eye = leye.detectMultiScale(gray)
            right_eye = reye.detectMultiScale(gray)
            # Detect the faces
            # faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            # Draw the rectangle around each face
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            if not success:
                break
            else:
                for (x, y, w, h) in right_eye:
                    r_eye = frame[y:y + h, x:x + w]
                    count = count + 1
                    r_eye = cv2.cvtColor(r_eye, cv2.COLOR_BGR2GRAY)
                    r_eye = cv2.resize(r_eye, (24, 24))
                    r_eye = r_eye / 255
                    r_eye = r_eye.reshape(24, 24, -1)
                    r_eye = np.expand_dims(r_eye, axis=0)
                    rpred = model.predict_classes(r_eye)

                for (x, y, w, h) in left_eye:
                    l_eye = frame[y:y + h, x:x + w]
                    count = count + 1
                    l_eye = cv2.cvtColor(l_eye, cv2.COLOR_BGR2GRAY)
                    l_eye = cv2.resize(l_eye, (24, 24))
                    l_eye = l_eye / 255
                    l_eye = l_eye.reshape(24, 24, -1)
                    l_eye = np.expand_dims(l_eye, axis=0)
                    lpred = model.predict_classes(l_eye)

                if (rpred[0] == 0 and lpred[0] == 0):
                    score = score + 1
                    cv2.putText(frame, "eye_closed", (10, height - 20),
                                font, 1, (255, 255, 255), 1, cv2.LINE_AA)

                else:
                    score = score - 1
                    cv2.putText(frame, "eye_open", (10, height - 20),
                                font, 1, (255, 255, 255), 1, cv2.LINE_AA)

                if (score < 0):
                    score = 0
                cv2.putText(frame, 'Score:' + str(score), (150, height - 20),
                            font, 1, (255, 255, 255), 1, cv2.LINE_AA)

                if (score > 15):
                    # person is feeling sleepy so we beep the alarm

                    try:
                        sound.play()
                        cv2.putText(frame, "DROWSINESS ALERT..!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255),
                                    2)

                    except:  # isplaying = False
                        pass
                    if (thicc < 16):
                        thicc = thicc + 2
                    else:
                        thicc = thicc - 2
                        if (thicc < 2):
                            thicc = 2
                    cv2.rectangle(frame, (0, 0), (width, height),
                                  (0, 0, 255), thicc)
                # cv2.imshow('frame', frame)

                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

    except Exception as e:
        print(e)
        tb = sys.exc_info()[2]
        print(tb.tb_lineno)


@app.route("/stopAlarm")
def stopAlarm():
    
    return render_template("user_home.html")

if __name__ == '__main__':
    app.run(host="localhost", port=1357, debug=True)
