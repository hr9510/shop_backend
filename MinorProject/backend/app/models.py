from . import db
from werkzeug.security import generate_password_hash, check_password_hash

class teacherRegistration(db.Model):
    __tablename__ = "Teacher_registration"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable= False, unique = True)
    password = db.Column(db.String(200), nullable= False)

    def encryptPassword(self, password):
        self.password = generate_password_hash(password)
    def checkPassword(self, password):
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f"<teacherRegistration{self.id}/>"
    
class studentRegistration(db.Model):
    __tablename__ = "Student_registration"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30), nullable=False)
    rollno = db.Column(db.String(30), unique = True, nullable= False)
    email = db.Column(db.String(30), nullable= False)
    password = db.Column(db.String(200), nullable= False)
    face_encoding = db.Column(db.PickleType)

    def encrypt_password(self, password):
        return generate_password_hash(password)
    
    def decrypt_password(self, password):
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f"<studentRegistration{self.id}/>"

class Code(db.Model):
    __tablename__ = "Code_saver"
    id = db.Column(db.Integer, primary_key=True)
    codeWord = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    className = db.Column(db.String(50), nullable=False)
    
    teacherEmail = db.Column(db.String(30), db.ForeignKey("Teacher_registration.email"), nullable=False)

    teacher = db.relationship("teacherRegistration", backref=db.backref("codes", lazy=True))

    def __repr__(self):
        return f"<Code {self.id}>"

class AttendenceData(db.Model):
    __tablename__ = "AttendenceData"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    rollno = db.Column(db.String(30), unique = True)
    name = db.Column(db.String(30))
    subject = db.Column(db.String, nullable = False)
    className = db.Column(db.String, nullable = False)

    def __repr__(self):
        return f"<AttendenceData{self.rollno}/>"
    
class Create_schedule(db.Model):
    __tablename__ = "Create_schedule"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    email = db.Column(db.String(30))
    className = db.Column(db.String(30))
    day = db.Column(db.String(20))
    subject = db.Column(db.String(50))
    start_time = db.Column(db.Time, nullable = False)
    end_time = db.Column(db.Time, nullable = False)

    def __repr__(self):
        return f"<Create_schedule{self.id}/>"

