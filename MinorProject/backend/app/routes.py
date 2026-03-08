from .models import db, Code,AttendenceData, Create_schedule, teacherRegistration,studentRegistration, generate_password_hash
from flask import request, jsonify, Blueprint, Response,send_file
from datetime import datetime
import base64
import face_recognition
import os
import io
import pandas as pd

main_bp = Blueprint("main_bp", __name__)

@main_bp.route("/verifyFace", methods=["POST"])
def verify_face():
    try:
        data = request.get_json()
        email = data.get("email")
        live_image_b64 = data.get("image")

        if not email or not live_image_b64:
            return jsonify({"message": "Missing data"}), 400

        student = studentRegistration.query.filter_by(email=email).first()
        if not student:
            return jsonify({"message": "Student not found"}), 404

        stored_image_b64 = student.face_encoding.split(",")[1]
        stored_image_bytes = base64.b64decode(stored_image_b64)
        with open("stored_face.jpg", "wb") as f:
            f.write(stored_image_bytes)

        live_image_bytes = base64.b64decode(live_image_b64.split(",")[1])
        with open("live_face.jpg", "wb") as f:
            f.write(live_image_bytes)

        stored_img = face_recognition.load_image_file("stored_face.jpg")
        live_img = face_recognition.load_image_file("live_face.jpg")

        stored_encodings = face_recognition.face_encodings(stored_img)
        live_encodings = face_recognition.face_encodings(live_img)

        if not stored_encodings or not live_encodings:
            return jsonify({"message": "No face detected in image"}), 400

        match = face_recognition.compare_faces(
            [stored_encodings[0]], live_encodings[0], tolerance=0.5
        )[0]

        os.remove("stored_face.jpg")
        os.remove("live_face.jpg")

        if match:
            return jsonify({"message": "Face Matched ✅"})
        else:
            return jsonify({"message": "Face Not Matched ❌"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_bp.route('/export_excel', methods=["GET"])
def export_excel():
    records = AttendenceData.query.all()
    if not records:
        return jsonify({"message" : "No attendence found"})

    dataList = [{"rollno": d.rollno, "name": d.name} for d in records]
    df = pd.DataFrame(dataList)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        worksheet = workbook.add_worksheet('Attendance')
        bold = workbook.add_format({'bold': True, 'font_size': 14})

        now = datetime.now()
        worksheet.write('A1', 'Date :', bold)
        worksheet.write('B1', now.strftime('%Y-%m-%d'), bold)
        worksheet.write('D1', 'Day :', bold)
        worksheet.write('E1', now.strftime('%A'), bold)
        worksheet.write('G1', 'Subject:', bold)
        worksheet.write('H1', records[0].subject, bold)
        worksheet.write('J1', 'Class :', bold)
        worksheet.write('K1', records[0].className, bold)

        df.to_excel(writer, sheet_name='Attendance', startrow=2, index=False)

    output.seek(0)
    return send_file(
        output,
        download_name=f"attendance_ {records[0].subject}_{now.strftime('%Y-%m-%d')}.xlsx",
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@main_bp.route("/", methods=["POST"])
def SetCode():
    data = request.get_json()
    if not data :
        return jsonify({"message" : "Please Post some data to store into database"})
    newCode = Code(codeWord = data.get("code"), subject= data.get("subject"), className = data.get("className"))
    db.session.add(newCode)
    db.session.commit()
    return jsonify({"message" : "Code saved successfully" })

@main_bp.route("/getCode", methods=["GET"])
def GetCode():
    code = Code.query.all()
    if not code:
        return jsonify({"message" : "No code available"})
    codeList = [{
    "id": c.id,
    "code": c.codeWord,
    "subject": c.subject,
    "className": c.className,
    "teacherEmail" : c.teacherEmail
}for c in code]
    
    return jsonify(codeList)


@main_bp.route("/updateCode", methods=["PUT"])
def updateCode():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Send some data"}), 400

    try:
        oldCode = Code.query.filter_by(teacherEmail=data.get("email")).first()
        if not oldCode:
            return jsonify({"message": "No code record"}), 404

        oldCode.codeWord  = data.get("result")
        oldCode.subject   = data.get("subject")
        oldCode.className = data.get("className")

        db.session.commit()

        return jsonify({"message": "Code updated Successfully"}), 200

    except Exception as e:
        db.session.rollback() 
        return jsonify({"message": "Update failed", "error": str(e)}), 500


@main_bp.route("/markAttendence", methods=["POST"])
def markAttendence():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data received"}), 400

    user = data.get("userData")
    if not user:
        return jsonify({"message": "Missing userData field"}), 400

    new_attendance = AttendenceData(
        rollno=user.get("rollno"),
        name=user.get("name"),
        className=data.get("className"),
        subject=data.get("subject")
    )
    db.session.add(new_attendance)
    db.session.commit()

    return jsonify({"message": "Attendance marked successfully!"})


@main_bp.route("/getAttendence", methods=["GET"])
def getAttendence():
    data = AttendenceData.query.all()
    if not data:
        return jsonify({"message" : "Send some data first"})
    dataList = [{
        "id" : d.id,
        "rollno" : d.rollno,
        "name" : d.name,
        "className" : d.className,
        "subject" : d.subject
    }for d in data]
    return jsonify(dataList)

@main_bp.route("/deleteAttendence", methods=["GET"])
def deleteAttendence ():
    attendence = AttendenceData.query.all()
    if attendence:
        for a in attendence:
            db.session.delete(a)
        db.session.commit()
        return jsonify({"message" : "Attendence deleted successfully!"})
    return jsonify({"message" : "No data available"})

@main_bp.route("/Creating_schedule", methods=["POST"])
def creatingSchedule():
    data = request.get_json()
    if not data:
        return jsonify ({"message" : "send some data first"})
    st = datetime.strptime(data.get("start_time"), "%H:%M").time()
    et = datetime.strptime(data.get("end_time"), "%H:%M").time()
    addSession = Create_schedule(email = data.get("email"),className = data.get("className"), day = data.get("day"), subject = data.get("subject"), start_time = st, end_time = et)
    db.session.add(addSession)
    db.session.commit()
    return jsonify({"message" : "Schedule added successfully!"})

@main_bp.route("/getSchedule", methods=["GET"])
def getSchedule():
    data = Create_schedule.query.all()
    if not data:
        return jsonify({"message": "no data available"}), 404

    data_list = []
    for d in data:
        day = datetime.now().strftime("%A")
        curr_time = datetime.now().strftime("%H:%M:%S")
        start_time_str = d.start_time.strftime("%H:%M:%S") if d.start_time else None
        end_time_str = d.end_time.strftime("%H:%M:%S") if d.end_time else None

        data_list.append({
            "id": d.id,
            "className": d.className,
            "day" : d.day,
            "email": d.email,
            "subject": d.subject,
            "start_time": start_time_str,
            "end_time": end_time_str,
            "curr_time" : curr_time,
            "curr_day" : day
        })
    return jsonify(data_list), 200

@main_bp.route("/deleteSchedule", methods=["GET"])
def deleteSchedule():
    dele = Create_schedule.query.all()
    for d in dele:
        db.session.delete(d)
    db.session.commit()
    return jsonify({"message" : "schedule delete successfully!"})


@main_bp.route("/registerTeacher", methods=["POST"])
def registerTeacher():
    data = request.get_json()
    if not data:
        return jsonify({"message" : "Please Post some data to store into database"})
    register = teacherRegistration(name = data.get("name"), email = data.get("email"))
    register.encryptPassword(data.get("password"))
    db.session.add(register)
    db.session.commit()

    newCode = Code(codeWord = "!@#$%^&*()_+[]{[]}|;:',.<>?/~`-=", subject= "nothing", className = "nothing", teacherEmail = register.email)
    db.session.add(newCode)
    db.session.commit()
    return jsonify({"message" : "Teacher Registered Successfully!"})

@main_bp.route("/getTeacher", methods=["GET"])
def getTeacher():
    data = teacherRegistration.query.all()
    if not data:
        return jsonify({"message" : "Send some data first"})
    data_List = [{
        "id" : d.id,
        "name" : d.name,
        "email" : d.email
    } for d in data]
    return jsonify(data_List)

@main_bp.route("/deleteTeacher", methods=["GET"])
def deleteTeacher():
    dele = teacherRegistration.query.all()
    for d in dele:
        db.session.delete(d)
    db.session.commit()
    return jsonify({"message" : "Teacher delete successfully!"})

@main_bp.route("/registerStudent", methods=["POST"])
def registerStudent():
    data = request.get_json()
    userData = data.get("userData")
    if not data:
        return jsonify({"message": "Please send valid data"}), 400

    register = studentRegistration(
        name=userData.get("name"),
        email=userData.get("email"),
        rollno=userData.get("rollno"),
        face_encoding = data.get("image")
    )
    register.encrypt_password(userData.get("password"))
    db.session.add(register)
    db.session.commit()

    return jsonify({"message": "Student Registered Successfully!"})


@main_bp.route("/getStudent", methods=["GET"])
def getStudent():
    data = studentRegistration.query.all()
    if not data:
        return jsonify({"message" : "Send some data first"})
    data_List = [{
        "id" : d.id,
        "name" : d.name,
        "rollno" : d.rollno,
        "email" : d.email,
        "face_encoding" : d.face_encoding
    } for d in data]
    return jsonify(data_List)

import base64

@main_bp.route('/showFace/<int:student_id>')
def show_face(student_id):
    student = studentRegistration.query.get(student_id)
    if not student:
        return "Student not found!", 404

    image_data = base64.b64decode(student.face_encoding.split(',')[1])
    return Response(image_data, mimetype='image/jpeg')