# from flask import Flask, render_template, request,jsonify,Response
import backend.dbmongo as dbmongo
import backend.fpwd as fpwd
import body
from flask import Flask, render_template, Response, jsonify, request
import cv2
#from yolov5 import YOLOv5
import torch
import webbrowser 

username, email, password, disability, role, dob, slink, llink, glink, bio,gender = "", "", "", "", "", "", "", "", "", "", ""
video_camera = None
global_frame = None
image, pred_img,original,crop_bg,label = None, None, None, None, None

#body.cap.release()

app = Flask(__name__)

#Index Page
@app.route('/home')
def index():
    #body.cap.release()
    return render_template('index.html')

@app.route("/label")  #for label
def label_text():
    return jsonify(label)

@app.route("/translate") #for translation
def translate():
    body.cap = body.cv2.VideoCapture(0, cv2.CAP_DSHOW)
    txt=label_text()
    return render_template('video_out.html',txt=txt.json)
    
#model = YOLO("yolov5su.pt")
#model = YOLOv5("signLang/weights/best.pt")
#model = torch.hub.load('ultralytics/yolov5', 'custom', path='signLang/weights/best.pt', force_reload=True)
# def gen_vid():     # Video Stream
#     global video_camera 
#     global global_frame 
#     global label 
#     while True:
#         global image, pred_img,original,crop_bg,name
#         image, pred_img,original,crop_bg,name= body.collectData()
#         if name != None:
#             label = name
#         else:
#             label = "--"
#         frame = cv2.imencode('.jpg', image)[1].tobytes()
#         if frame != None:
#             global_frame = frame
#             yield (b'--frame\r\n'
#                     b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
#         else:
#             yield (b'--frame\r\n'
#                             b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')

# def gen_vid():
#     if body.cap is not None:
#         body.cap.release()
#     body.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
#     while True:
#         ret, frame = body.cap.read()
#         if not ret:
#             continue

#         frame = cv2.imencode('.jpg', frame)[1].tobytes()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def gen_vid():
    global label

    if body.cap is not None:
        body.cap.release()

    body.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    while True:
        # Get frame + prediction from body.collectData()
        image, pred_img, original, crop_bg, name = body.collectData()

        # Update predicted label
        if name:
            label = name
        else:
            label = "--"

        # Send frame to browser
        frame = cv2.imencode('.jpg', image)[1].tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route("/video")    # Video page
def video():
    return Response(gen_vid(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')  
  

@app.route("/about")    # About page
def about():
    #body.cap.release()
    return render_template('about_us.html')

@app.route("/signup")   # Sign up page
def sign_up():
    #body.cap.release()
    return render_template('sign_up.html')

@app.route("/") #for login page
def login():
    #body.cap.release()
    return render_template('login.html',userinfo=None,accept=None)

@app.route("/profile")      # Profile page
def profile():
    #body.cap.release()
    userinfo=dbmongo.show(email)
    return render_template('profile.html',userinfo=userinfo)

@app.route("/choice")       # Choice page
def choice():
    return render_template('choice.html')

@app.route("/audio")        # Audio page
def audio():
    #body.cap.release()
    return render_template('audio_out.html')

@app.route('/validate', methods=['POST'])
def validate_sign():
    email = request.form['email']
    password = request.form['password']
    if dbmongo.validate(email,password):
        userinfo=dbmongo.show(email)
        return render_template('login.html',accept="success",userinfo=userinfo,email=email,password=password)
    else:
        return render_template('login.html',accept="failed",userinfo=None,email=email,password=None)

@app.route('/signup', methods=['POST'])
def getvalue():
    global username, email, password, disability, role,gender
    username = request.form['name']
    email = request.form['email']
    password = request.form['password']
    disability = request.form['inputDisability']
    role = request.form['inputRole']
    gender = request.form['gender']
    print(username, email, password, disability, role,gender)
    if username and email and password and disability and role:
        if not dbmongo.check(email):
            print("Email does exist")
            accept="exist"
            return render_template('sign_up.html',accept=accept,email=email,username=username)
        else:
            fpwd.otp(email)
            print("Email does not exist")
            return render_template('sign_up.html',accept="otp",email=email,username=username)
    else:
            accept="failed"
            return render_template('sign_up.html',accept=accept,email=email,username=username)
        
@app.route('/otp', methods=['POST'])
def otp():
    print("OTP: ")
    print(fpwd.otp)
    otp = request.form['otp']
    print(otp)
    print(username, email, password, disability, role,gender)
    slink = "https://www.facebook.com/"
    llink = "https://www.linkedin.com/"
    glink = "https://www.github.com/"
    if otp == str(fpwd.otp):
        if dbmongo.insert(username,email,password,disability,role,dob, slink, llink, glink, bio,gender):
            accept="success"
            return render_template('sign_up.html',accept=accept,email=email,username=username)
    else:
        accept="otp-failed"
        print("OTP failed")
        return render_template('sign_up.html',accept=accept,email=email,username=username)

@app.route('/forgot')
def forgot():
    return render_template('login.html',accept="forgot",userinfo=None)    

@app.route('/forgotpass', methods=['POST'])
def forgotpass():
    email = request.form['f_email']
    if not dbmongo.check(email):
        fpwd.sendmail(email)
        print("Email sent")
        accept="sent"
        return render_template('login.html',accept=accept,userinfo=None,email=email,password=None)
    else:
        print("Email not sent")
        accept="not"
        return render_template('login.html',accept=accept,userinfo=None,email=email,password=None)
    
@app.route('/changepass', methods=['POST'])
def changepass():
    password = request.form['new_password']
    email = request.form['chg_email']
    print(password,email)
    dbmongo.updatepwd(email,password)
    userinfo=dbmongo.show(email)
    return render_template('profile.html',userinfo=userinfo)

@app.route('/update', methods=['POST'])
def update():
    name = request.form['name']
    email = request.form['up_email']
    role = request.form['role']
    disability = request.form['disability']
    dob = request.form['dob']
    bio = request.form['bio']
    slink = request.form['slink']
    llink = request.form['llink']
    glink = request.form['glink']
    gender = request.form['gender']
    print(name,email,role,disability,dob,bio,slink,llink,glink,gender)     
    dbmongo.update(name,email,disability,role,dob,slink,llink,glink,bio,gender)
    userinfo=dbmongo.show(email)
    return render_template('profile.html',userinfo=userinfo)

webbrowser.open('http://127.0.0.1:5000/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True ,port=5000,debug=False)
    


# from flask import Flask, render_template, request, jsonify, Response
# import backend.mongo as mongo
# import backend.fpwd as fpwd
# import cv2
# import webbrowser
# from ultralytics import YOLO
# import torch

# username, email, password, disability, role, dob, slink, llink, glink, bio, gender = "", "", "", "", "", "", "", "", "", "", ""
# label = "--"

# app = Flask(__name__)

# # ------------------ ROUTES ------------------

# @app.route('/home')
# def index():
#     return render_template('index.html')

# @app.route("/label")
# def label_text():
#     return jsonify(label)

# @app.route("/translate")
# def translate():
#     txt = label_text()
#     return render_template('video_out.html', txt=txt.json)

# # ---------------- LOAD YOLO MODEL ------------------

# #model = YOLO("modelS/weights/best.pt")  # Using your trained best.pt
# #model = torch.hub.load('ultralytics/yolov5', 'custom', path='modelS/weights/best.pt', force_reload=True)
# model = YOLO("yolov5su.pt")

# # ------------------ VIDEO STREAM ------------------

# def gen_vid():
#     global label
#     cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             continue

#         # Run YOLOv5 inference
#         results = model(frame)  # frame from OpenCV

#         # Reset label
#         label = "--"

#         # If any detections
#         if len(results.xyxy[0]) > 0:
#             for *xyxy, conf, cls in results.xyxy[0]:  # xyxy: coordinates, conf: confidence, cls: class index
#                 if conf.item() > 0.7:
#                     cls = int(cls.item())
#                     label = results.names[cls]

#                     # Draw bounding box
#                     xyxy = [int(x.item()) for x in xyxy]
#                     cv2.rectangle(frame, (xyxy[0], xyxy[1]), (xyxy[2], xyxy[3]), (0, 255, 0), 2)
#                     cv2.putText(frame, label, (xyxy[0], xyxy[1]-10),
#                                 cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
#         else:
#             label = "--"

#         # Encode frame as JPEG
#         ok, buffer = cv2.imencode('.jpg', frame)
#         if not ok:
#             continue

#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n\r\n')


# @app.route("/video")
# def video():
#     return Response(gen_vid(),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')

# # ------------------ REGULAR ROUTES ------------------

# @app.route("/about")
# def about():
#     return render_template('about_us.html')

# @app.route("/signup")
# def sign_up():
#     return render_template('sign_up.html')

# @app.route("/")
# def login():
#     return render_template('login.html', userinfo=None, accept=None)

# @app.route("/profile")
# def profile():
#     userinfo = mongo.show(email)
#     return render_template('profile.html', userinfo=userinfo)

# @app.route("/choice")
# def choice():
#     return render_template('choice.html')

# @app.route("/audio")
# def audio():
#     return render_template('audio_out.html')

# # ------------------ VALIDATION ------------------

# @app.route('/validate', methods=['POST'])
# def validate_sign():
#     email = request.form['email']
#     password = request.form['password']
#     if mongo.validate(email, password):
#         userinfo = mongo.show(email)
#         return render_template('login.html', accept="success", userinfo=userinfo,
#                                email=email, password=password)
#     else:
#         return render_template('login.html', accept="failed", userinfo=None,
#                                email=email, password=None)

# @app.route('/signup', methods=['POST'])
# def getvalue():
#     global username, email, password, disability, role, gender
#     username = request.form['name']
#     email = request.form['email']
#     password = request.form['password']
#     disability = request.form['inputDisability']
#     role = request.form['inputRole']
#     gender = request.form['gender']

#     if username and email and password and disability and role:
#         if not mongo.check(email):
#             accept = "exist"
#             return render_template('sign_up.html', accept=accept, email=email, username=username)
#         else:
#             fpwd.otp(email)
#             return render_template('sign_up.html', accept="otp", email=email, username=username)
#     else:
#         return render_template('sign_up.html', accept="failed", email=email, username=username)

# @app.route('/otp', methods=['POST'])
# def otp():
#     global dob, slink, llink, glink, bio, gender
#     otp = request.form['otp']

#     slink = "https://www.facebook.com/"
#     llink = "https://www.linkedin.com/"
#     glink = "https://www.github.com/"

#     if otp == str(fpwd.otp):
#         if mongo.insert(username, email, password, disability, role, dob, slink, llink, glink, bio, gender):
#             return render_template('sign_up.html', accept="success", email=email, username=username)
#     return render_template('sign_up.html', accept="otp-failed", email=email, username=username)

# @app.route('/forgot')
# def forgot():
#     return render_template('login.html', accept="forgot", userinfo=None)

# @app.route('/forgotpass', methods=['POST'])
# def forgotpass():
#     email = request.form['f_email']
#     if not mongo.check(email):
#         fpwd.sendmail(email)
#         return render_template('login.html', accept="sent", userinfo=None, email=email, password=None)
#     else:
#         return render_template('login.html', accept="not", userinfo=None, email=email, password=None)

# @app.route('/changepass', methods=['POST'])
# def changepass():
#     password = request.form['new_password']
#     email = request.form['chg_email']
#     mongo.updatepwd(email, password)
#     userinfo = mongo.show(email)
#     return render_template('profile.html', userinfo=userinfo)

# @app.route('/update', methods=['POST'])
# def update():
#     name = request.form['name']
#     email = request.form['up_email']
#     role = request.form['role']
#     disability = request.form['disability']
#     dob = request.form['dob']
#     bio = request.form['bio']
#     slink = request.form['slink']
#     llink = request.form['llink']
#     glink = request.form['glink']
#     gender = request.form['gender']

#     mongo.update(name, email, disability, role, dob, slink, llink, glink, bio, gender)
#     userinfo = mongo.show(email)
#     return render_template('profile.html', userinfo=userinfo)

# # ---------------- AUTO OPEN BROWSER ----------------

# webbrowser.open('http://127.0.0.1:5000/')

# # ---------------- RUN APP ----------------

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', threaded=True, port=5000, debug=False)
