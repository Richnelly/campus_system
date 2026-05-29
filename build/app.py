import os
from functools import wraps

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import date


app = Flask(__name__)
app.config["SECRET_KEY"] = "demo-secret-key-change-later"
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2MB max upload size
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Demo users. This data resets when the app restarts.
USERS = {
    "admin1": {
        "password": generate_password_hash("admin123"),
        "role": "admin",
        "name": "Admin User",
        "email": "admin@example.com",
        "phone": "",
        "department": "Administration",
        "student_id": "",
        "address": "",
        "city": "",
        "is_active": True,
    },
    "staff1": {
        "password": generate_password_hash("staff123"),
        "role": "staff",
        "name": "Staff User",
        "email": "staff@example.com",
        "phone": "",
        "department": "Computer Science",
        "student_id": "EMP001",
        "address": "",
        "city": "",
        "is_active": True,
    },
    "student1": {
        "password": generate_password_hash("student123"),
        "role": "student",
        "name": "Student User",
        "email": "student@example.com",
        "phone": "",
        "department": "Computer Science",
        "student_id": "STU2024001",
        "address": "",
        "city": "",
        "is_active": True,
    },
}

COURSES = [
    {
        "code": "CS101",
        "name": "Introduction to Programming",
        "credits": 4,
        "enrolled": 87,
        "instructor": "Dr. John Mwangi",
        "time": "Mon 10:00",
        "room": "CS Lab-1",
    },
    {
        "code": "BUS201",
        "name": "Principles of Marketing",
        "credits": 3,
        "enrolled": 54,
        "instructor": "Prof. Fatima Ali",
        "time": "Tue 14:00",
        "room": "LT-04",
    },
    {
        "code": "ENG305",
        "name": "Structural Analysis",
        "credits": 4,
        "enrolled": 32,
        "instructor": "Mr. David Kimaro",
        "time": "Wed 09:00",
        "room": "LT-12",
    },
    {
        "code": "BIO110",
        "name": "Cell Biology",
        "credits": 3,
        "enrolled": 68,
        "instructor": "Dr. Sarah Chen",
        "time": "Thu 11:00",
        "room": "Bio Lab-2",
    },
]

STUDENT_RESULTS = {
    "student1": [
        {
            "course_code": "CS101",
            "course_name": "Introduction to Programming",
            "credits": 4,
            "coursework": 34,
            "exam": 51,
            "semester": "Semester 2",
            "academic_year": "2025/2026",
        },
        {
            "course_code": "BUS201",
            "course_name": "Principles of Marketing",
            "credits": 3,
            "coursework": 30,
            "exam": 46,
            "semester": "Semester 2",
            "academic_year": "2025/2026",
        },
        {
            "course_code": "ENG305",
            "course_name": "Structural Analysis",
            "credits": 4,
            "coursework": 28,
            "exam": 42,
            "semester": "Semester 2",
            "academic_year": "2025/2026",
        },
        {
            "course_code": "BIO110",
            "course_name": "Cell Biology",
            "credits": 3,
            "coursework": 24,
            "exam": 33,
            "semester": "Semester 2",
            "academic_year": "2025/2026",
        },
    ]
}

COURSE_STUDENTS = {
    "CS101": [
        {"id": "STU2024001", "name": "Alice Mwangi"},
        {"id": "STU2024002", "name": "Brian Otieno"},
        {"id": "STU2024003", "name": "Cynthia Amina"},
        {"id": "STU2024004", "name": "Daniel Kiptoo"},
    ],
    "BUS201": [
        {"id": "STU2024005", "name": "Esther Njeri"},
        {"id": "STU2024006", "name": "Fredrick Kamau"},
        {"id": "STU2024007", "name": "Grace Wanjiru"},
    ],
    "ENG305": [
        {"id": "STU2024008", "name": "Hassan Omar"},
        {"id": "STU2024009", "name": "Irene Wangari"},
        {"id": "STU2024010", "name": "Joseph Mutua"},
    ],
    "BIO110": [
        {"id": "STU2024011", "name": "Khadija Yusuf"},
        {"id": "STU2024012", "name": "Lawrence Mwai"},
        {"id": "STU2024013", "name": "Mary Atieno"},
    ],
}

ATTENDANCE_RECORDS = {}
GRADE_RECORDS = {}
STAFF_SCHEDULES = {}
ASSIGNMENTS = {}

STUDENTS = [
    {
        "id": "STU2024001",
        "name": "Alice Mwangi",
        "gender": "Female",
        "dob": "2004-05-14",
        "email": "alice.mwangi@uni.edu",
        "phone": "0712345678",
        "department": "Computer Science",
        "course": "CS101",
        "year": "2",
        "address": "12 University Way, Nairobi",
        "guardian": "James Mwangi - 0711 222 333",
        "profile_image": "https://i.pravatar.cc/150?img=32",
        "status": "Active",
    },
    {
        "id": "STU2024002",
        "name": "Brian Otieno",
        "gender": "Male",
        "dob": "2003-08-20",
        "email": "brian.otieno@uni.edu",
        "phone": "0713344556",
        "department": "Business",
        "course": "BUS201",
        "year": "3",
        "address": "45 Commerce Lane, Nairobi",
        "guardian": "Susan Otieno - 0713 123 456",
        "profile_image": "https://i.pravatar.cc/150?img=20",
        "status": "Active",
    },
    {
        "id": "STU2024003",
        "name": "Cynthia Amina",
        "gender": "Female",
        "dob": "2002-12-02",
        "email": "cynthia.amina@uni.edu",
        "phone": "0714455667",
        "department": "Engineering",
        "course": "ENG305",
        "year": "4",
        "address": "77 Engineering Road, Nairobi",
        "guardian": "Fatma Amina - 0714 222 333",
        "profile_image": "https://i.pravatar.cc/150?img=45",
        "status": "Active",
    },
    {
        "id": "STU2024004",
        "name": "David Kimaro",
        "gender": "Male",
        "dob": "2005-01-28",
        "email": "david.kimaro@uni.edu",
        "phone": "0715566778",
        "department": "Biology",
        "course": "BIO110",
        "year": "1",
        "address": "23 Green Valley, Nairobi",
        "guardian": "Mary Kimaro - 0715 333 444",
        "profile_image": "https://i.pravatar.cc/150?img=12",
        "status": "Active",
    }
]

STAFF_MEMBERS = [
    {
        "id": "EMP001",
        "name": "Dr. John Mwangi",
        "email": "john.mwangi@uni.edu",
        "phone": "0721000111",
        "department": "Computer Science",
        "course_assignments": ["CS101"],
        "role": "Lecturer",
        "profile_image": "https://i.pravatar.cc/150?img=5",
        "address": "99 Tech Avenue, Nairobi",
        "status": "Active",
    },
    {
        "id": "EMP002",
        "name": "Prof. Fatima Ali",
        "email": "fatima.ali@uni.edu",
        "phone": "0721000222",
        "department": "Business",
        "course_assignments": ["BUS201"],
        "role": "Lecturer",
        "profile_image": "https://i.pravatar.cc/150?img=6",
        "address": "1 Commerce Street, Nairobi",
        "status": "Active",
    },
    {
        "id": "EMP003",
        "name": "Mr. David Kimaro",
        "email": "david.kimaro@uni.edu",
        "phone": "0721000333",
        "department": "Engineering",
        "course_assignments": ["ENG305"],
        "role": "Lecturer",
        "profile_image": "https://i.pravatar.cc/150?img=7",
        "address": "18 Engineering Lane, Nairobi",
        "status": "Active",
    }
]

DEPARTMENTS = [
    {
        "id": "CS",
        "name": "Computer Science",
        "hod": "Dr. John Mwangi",
        "active": True,
        "student_count": 280,
        "staff_count": 12,
    },
    {
        "id": "BUS",
        "name": "Business",
        "hod": "Prof. Fatima Ali",
        "active": True,
        "student_count": 216,
        "staff_count": 10,
    },
    {
        "id": "ENG",
        "name": "Engineering",
        "hod": "Mr. David Kimaro",
        "active": True,
        "student_count": 142,
        "staff_count": 9,
    }
]

FEE_PAYMENTS = [
    {
        "id": "PAY001",
        "student_id": "STU2024001",
        "student_name": "Alice Mwangi",
        "amount": 4500,
        "date": "2026-05-10",
        "payment_method": "Card",
        "status": "Paid",
        "balance": 1500,
    },
    {
        "id": "PAY002",
        "student_id": "STU2024002",
        "student_name": "Brian Otieno",
        "amount": 3000,
        "date": "2026-05-14",
        "payment_method": "Cash",
        "status": "Partial",
        "balance": 2500,
    }
]

RESULT_RECORDS = [
    {
        "student_id": "STU2024001",
        "student_name": "Alice Mwangi",
        "course_code": "CS101",
        "course_name": "Introduction to Programming",
        "score": 85,
        "grade": "A",
        "gpa": 4.0,
        "semester": "Semester 2",
        "approved": False,
    },
    {
        "student_id": "STU2024002",
        "student_name": "Brian Otieno",
        "course_code": "BUS201",
        "course_name": "Principles of Marketing",
        "score": 72,
        "grade": "A",
        "gpa": 4.0,
        "semester": "Semester 2",
        "approved": True,
    }
]


def find_student_index(student_id):
    for index, student in enumerate(STUDENTS):
        if student["id"] == student_id:
            return index
    return None


def find_staff_index(staff_id):
    for index, staff in enumerate(STAFF_MEMBERS):
        if staff["id"] == staff_id:
            return index
    return None


def find_department_index(department_id):
    for index, department in enumerate(DEPARTMENTS):
        if department["id"] == department_id:
            return index
    return None


def grade_letter(score):
    try:
        score = float(score)
    except (TypeError, ValueError):
        return "F"
    if score >= 70:
        return "A"
    if score >= 60:
        return "B"
    if score >= 50:
        return "C"
    if score >= 45:
        return "D"
    if score >= 40:
        return "E"
    return "F"


def calculate_gpa(scores):
    if not scores:
        return 0.0
    total = 0.0
    for grade in scores:
        total += {
            "A": 4.0,
            "B": 3.0,
            "C": 2.0,
            "D": 1.0,
            "E": 0.5,
            "F": 0.0,
        }.get(grade, 0.0)
    return round(total / len(scores), 2)


def attendance_summary():
    total_sessions = 0
    present_count = 0
    for records in ATTENDANCE_RECORDS.values():
        total_sessions += len(records)
        for record in records:
            present_count += sum(1 for item in record.get("attendance", []) if item.get("status") == "Present")
    if total_sessions == 0 or not STUDENTS:
        return 0.0
    possible = total_sessions * len(STUDENTS)
    return round((present_count / possible) * 100, 1)


@app.context_processor
def template_helpers():
    # Existing templates call csrf_token(). This keeps them working without Flask-WTF.
    return {"csrf_token": lambda: ""}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def current_user():
    username = session.get("username")
    if not username:
        return None
    return USERS.get(username)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        user = current_user()
        if not user:
            flash("Please login first", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            user = current_user()
            if not user:
                flash("Please login first", "warning")
                return redirect(url_for("login"))
            if user.get("role") not in roles:
                flash("Access denied for this account", "danger")
                return redirect(url_for("dashboard"))
            return view(*args, **kwargs)

        return wrapped_view

    return decorator


def find_course_index(code):
    code = code.upper()
    for index, course in enumerate(COURSES):
        if course["code"] == code:
            return index
    return None


def clean_course_data(data):
    code = data.get("code", "").strip().upper()
    name = data.get("name", "").strip()
    credits = int(data.get("credits", 3))
    enrolled = int(data.get("enrolled", 0))

    if not code or not name:
        raise ValueError("Course code and name are required")
    if credits < 1 or credits > 8:
        raise ValueError("Credits must be between 1 and 8")
    if enrolled < 0 or enrolled > 120:
        raise ValueError("Enrolled students must be between 0 and 120")

    return {
        "code": code,
        "name": name,
        "credits": credits,
        "enrolled": enrolled,
        "instructor": data.get("instructor", "Staff Lecturer").strip() or "Staff Lecturer",
        "time": data.get("time", "TBA").strip() or "TBA",
        "room": data.get("room", "TBA").strip() or "TBA",
    }


@app.route("/")
def index():
    if current_user():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = USERS.get(username)

        if user and user.get("is_active", True) and check_password_hash(user["password"], password):
            session["username"] = username
            session["user_id"] = username
            session["role"] = user["role"]
            session["name"] = user["name"]
            flash(f"Welcome, {user['name']}!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid username or password", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        email = request.form.get("email", "").strip()
        name = request.form.get("name", "").strip()
        role = request.form.get("role", "student").strip()

        if not all([username, password, confirm_password, email, name]):
            flash("All fields are required", "danger")
            return redirect(url_for("register"))

        if len(username) < 3:
            flash("Username must be at least 3 characters", "danger")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters", "danger")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for("register"))

        if username in USERS:
            flash("Username already exists", "danger")
            return redirect(url_for("register"))

        if any(user["email"].lower() == email.lower() for user in USERS.values()):
            flash("Email already registered", "danger")
            return redirect(url_for("register"))

        USERS[username] = {
            "password": generate_password_hash(password),
            "role": role if role in ["admin", "staff", "student"] else "student",
            "name": name,
            "email": email,
            "phone": "",
            "department": "",
            "student_id": "",
            "address": "",
            "city": "",
            "is_active": True,
        }

        flash("Account created successfully. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/dashboard")
@login_required
def dashboard():
    role = session.get("role")
    if role == "admin":
        return redirect(url_for("admin_dashboard"))
    if role == "staff":
        return redirect(url_for("staff_dashboard"))
    if role == "student":
        return redirect(url_for("student_dashboard"))

    flash("Role not recognized", "danger")
    return redirect(url_for("logout"))


@app.route("/admin")
@role_required("admin")
def admin_dashboard():
    return render_template(
        "admin panel.html",
        user=current_user(),
        courses=COURSES,
        students=STUDENTS,
        staff=STAFF_MEMBERS,
        departments=DEPARTMENTS,
        fees=FEE_PAYMENTS,
        results=RESULT_RECORDS,
        attendance=ATTENDANCE_RECORDS,
    )


@app.route("/staff")
@role_required("staff")
def staff_dashboard():
    return render_template("staff.html", user=current_user(), courses=COURSES)


@app.route("/student")
@role_required("student")
def student_dashboard():
    username = session.get("username")
    results = STUDENT_RESULTS.get(username, [])
    return render_template("student.html", user=current_user(), courses=COURSES, results=results)


@app.route("/api/courses")
@login_required
def api_courses():
    return jsonify(COURSES)


@app.route("/api/staff/attendance/<code>")
@role_required("staff")
def api_staff_attendance(code):
    code = code.upper()
    course = next((c for c in COURSES if c["code"] == code), None)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    students = list(COURSE_STUDENTS.get(code, []))
    records = ATTENDANCE_RECORDS.get(code, [])
    student_index = {student["id"]: student for student in students}
    name_index = {student["name"]: student for student in students}
    for record in records:
        for item in record.get("attendance", []):
            sid = item.get("student_id")
            name = item.get("name", "")
            if sid:
                if sid not in student_index:
                    student_index[sid] = {"id": sid, "name": name}
            elif name and name not in name_index:
                student_index[name] = {"id": name, "name": name}
    return jsonify({"course": course, "students": list(student_index.values()), "attendance": records})


@app.route("/api/staff/attendance/<code>", methods=["POST"])
@role_required("staff")
def api_staff_save_attendance(code):
    code = code.upper()
    course = next((c for c in COURSES if c["code"] == code), None)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    data = request.get_json(silent=True) or {}
    date_str = data.get("date", str(date.today()))
    attendance = data.get("attendance", [])
    if not isinstance(attendance, list):
        return jsonify({"error": "Attendance list is required"}), 400

    ATTENDANCE_RECORDS.setdefault(code, []).append({"date": date_str, "attendance": attendance})
    return jsonify({"message": "Attendance saved successfully", "course_code": code, "date": date_str})


@app.route("/api/staff/grades/<code>")
@role_required("staff")
def api_staff_grades(code):
    code = code.upper()
    course = next((c for c in COURSES if c["code"] == code), None)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    students = list(COURSE_STUDENTS.get(code, []))
    grades = list(GRADE_RECORDS.get(code, []))
    grade_index = {entry.get("student_id"): entry for entry in grades if entry.get("student_id")}

    for student in students:
        if student["id"] in grade_index:
            grade_index[student["id"]]["name"] = student["name"]

    for entry in grades:
        student_id = entry.get("student_id")
        student_name = entry.get("name")
        if student_id and student_id not in [s["id"] for s in students]:
            students.append({"id": student_id, "name": student_name or ""})
        elif not student_id and student_name:
            students.append({"id": student_name, "name": student_name})

    return jsonify({"course": course, "students": students, "grades": grades})


@app.route("/api/staff/grades/<code>", methods=["POST"])
@role_required("staff")
def api_staff_save_grades(code):
    code = code.upper()
    course = next((c for c in COURSES if c["code"] == code), None)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    data = request.get_json(silent=True) or {}
    grades = data.get("grades", [])
    if not isinstance(grades, list):
        return jsonify({"error": "Grades list is required"}), 400

    entries = GRADE_RECORDS.setdefault(code, [])
    for item in grades:
        student_id = item.get("student_id") or item.get("name")
        student_name = item.get("name") or ""
        score = item.get("score")
        grade = item.get("grade")

        if score is not None and score != "":
            try:
                score = float(score)
            except ValueError:
                score = None

        if student_id is None and not student_name:
            continue

        existing = next((entry for entry in entries if entry.get("student_id") == student_id), None)
        entry_data = {
            "student_id": student_id,
            "name": student_name,
            "score": score,
            "grade": grade,
        }

        if existing:
            existing.update(entry_data)
        else:
            entries.append(entry_data)

    return jsonify({"message": "Grades saved successfully", "course_code": code, "grades": entries})


@app.route("/api/staff/schedule")
@role_required("staff")
def api_staff_schedule():
    username = session.get("username")
    schedule = STAFF_SCHEDULES.get(username, [])
    return jsonify({"schedule": schedule, "courses": COURSES})


@app.route("/api/staff/schedule", methods=["POST"])
@role_required("staff")
def api_staff_save_schedule():
    username = session.get("username")
    data = request.get_json(silent=True) or {}
    day = data.get("day", "Monday").strip()
    time_slot = data.get("time", "").strip()
    course_code = data.get("course_code", "").upper().strip()
    room = data.get("room", "").strip() or "TBA"

    if not course_code or not time_slot:
        return jsonify({"error": "Course and time are required"}), 400

    course = next((c for c in COURSES if c["code"] == course_code), None)
    if not course:
        return jsonify({"error": "Course code not found"}), 404

    entry = {
        "day": day,
        "time": time_slot,
        "course_code": course_code,
        "course_name": course["name"],
        "room": room,
    }
    STAFF_SCHEDULES.setdefault(username, []).append(entry)
    return jsonify({"message": "Schedule entry saved", "entry": entry})


@app.route("/api/staff/assignments/<code>")
@role_required("staff")
def api_staff_assignments(code):
    code = code.upper()
    course = next((c for c in COURSES if c["code"] == code), None)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    assignments = ASSIGNMENTS.get(code, [])
    return jsonify({"course": course, "assignments": assignments})


@app.route("/api/staff/assignments/<code>", methods=["POST"])
@role_required("staff")
def api_staff_create_assignment(code):
    code = code.upper()
    course = next((c for c in COURSES if c["code"] == code), None)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    due_date = (data.get("due_date") or "").strip()
    total_marks = data.get("total_marks")
    description = (data.get("description") or "").strip()

    if not title or not due_date or not total_marks:
        return jsonify({"error": "Title, due date, and total marks are required"}), 400

    try:
        total_marks = int(total_marks)
    except (TypeError, ValueError):
        return jsonify({"error": "Total marks must be a number"}), 400

    assignments = ASSIGNMENTS.setdefault(code, [])
    next_id = str(max([int(item.get("id", 0)) for item in assignments] + [0]) + 1)
    assignment = {
        "id": next_id,
        "title": title,
        "due_date": due_date,
        "total_marks": total_marks,
        "description": description,
    }
    assignments.append(assignment)
    return jsonify({"message": "Assignment created successfully", "assignment": assignment}), 201


@app.route("/api/staff/assignments/<code>/<assignment_id>", methods=["PUT"])
@role_required("staff")
def api_staff_update_assignment(code, assignment_id):
    code = code.upper()
    course = next((c for c in COURSES if c["code"] == code), None)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    assignments = ASSIGNMENTS.setdefault(code, [])
    assignment = next((item for item in assignments if item.get("id") == assignment_id), None)
    if not assignment:
        return jsonify({"error": "Assignment not found"}), 404

    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    due_date = (data.get("due_date") or "").strip()
    total_marks = data.get("total_marks")
    description = (data.get("description") or "").strip()

    if not title or not due_date or not total_marks:
        return jsonify({"error": "Title, due date, and total marks are required"}), 400

    try:
        total_marks = int(total_marks)
    except (TypeError, ValueError):
        return jsonify({"error": "Total marks must be a number"}), 400

    assignment.update({"title": title, "due_date": due_date, "total_marks": total_marks, "description": description})
    return jsonify({"message": "Assignment updated successfully", "assignment": assignment})


@app.route("/api/staff/assignments/<code>/<assignment_id>", methods=["DELETE"])
@role_required("staff")
def api_staff_delete_assignment(code, assignment_id):
    code = code.upper()
    course = next((c for c in COURSES if c["code"] == code), None)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    assignments = ASSIGNMENTS.setdefault(code, [])
    index = next((i for i, item in enumerate(assignments) if item.get("id") == assignment_id), None)
    if index is None:
        return jsonify({"error": "Assignment not found"}), 404

    deleted = assignments.pop(index)
    return jsonify({"message": "Assignment deleted successfully", "assignment": deleted})


@app.route("/api/courses", methods=["POST"])
@role_required("admin")
def api_create_course():
    try:
        course = clean_course_data(request.get_json(silent=True) or {})
    except (TypeError, ValueError) as error:
        return jsonify({"error": str(error)}), 400

    if find_course_index(course["code"]) is not None:
        return jsonify({"error": "Course code already exists"}), 400

    COURSES.append(course)
    return jsonify(course), 201


@app.route("/api/courses/<code>", methods=["PUT"])
@role_required("admin")
def api_update_course(code):
    index = find_course_index(code)
    if index is None:
        return jsonify({"error": "Course not found"}), 404

    try:
        course = clean_course_data(request.get_json(silent=True) or {})
    except (TypeError, ValueError) as error:
        return jsonify({"error": str(error)}), 400

    duplicate_index = find_course_index(course["code"])
    if duplicate_index is not None and duplicate_index != index:
        return jsonify({"error": "Course code already exists"}), 400

    COURSES[index] = course
    return jsonify(course)


@app.route("/api/courses/<code>", methods=["DELETE"])
@role_required("admin")
def api_delete_course(code):
    index = find_course_index(code)
    if index is None:
        return jsonify({"error": "Course not found"}), 404

    deleted = COURSES.pop(index)
    return jsonify(deleted)


@app.route("/api/admin/students")
@role_required("admin")
def api_admin_students():
    return jsonify(STUDENTS)


@app.route("/api/admin/students", methods=["POST"])
@role_required("admin")
def api_admin_create_student():
    data = request.get_json(silent=True) or {}
    student_id = (data.get("id") or "").strip().upper()
    if not student_id:
        return jsonify({"error": "Student ID is required"}), 400
    if find_student_index(student_id) is not None:
        return jsonify({"error": "Student ID already exists"}), 400

    student = {
        "id": student_id,
        "name": data.get("name", "").strip(),
        "gender": data.get("gender", "").strip(),
        "dob": data.get("dob", "").strip(),
        "email": data.get("email", "").strip(),
        "phone": data.get("phone", "").strip(),
        "department": data.get("department", "").strip(),
        "course": data.get("course", "").strip(),
        "year": data.get("year", "").strip(),
        "address": data.get("address", "").strip(),
        "guardian": data.get("guardian", "").strip(),
        "profile_image": data.get("profile_image", "").strip(),
        "status": data.get("status", "Active").strip(),
    }
    STUDENTS.append(student)
    return jsonify(student), 201


@app.route("/api/admin/students/<student_id>", methods=["PUT"])
@role_required("admin")
def api_admin_update_student(student_id):
    index = find_student_index(student_id)
    if index is None:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json(silent=True) or {}
    STUDENTS[index].update({
        "name": data.get("name", STUDENTS[index]["name"]).strip(),
        "gender": data.get("gender", STUDENTS[index]["gender"]).strip(),
        "dob": data.get("dob", STUDENTS[index]["dob"]).strip(),
        "email": data.get("email", STUDENTS[index]["email"]).strip(),
        "phone": data.get("phone", STUDENTS[index]["phone"]).strip(),
        "department": data.get("department", STUDENTS[index]["department"]).strip(),
        "course": data.get("course", STUDENTS[index]["course"]).strip(),
        "year": data.get("year", STUDENTS[index]["year"]).strip(),
        "address": data.get("address", STUDENTS[index]["address"]).strip(),
        "guardian": data.get("guardian", STUDENTS[index]["guardian"]).strip(),
        "profile_image": data.get("profile_image", STUDENTS[index]["profile_image"]).strip(),
        "status": data.get("status", STUDENTS[index]["status"]).strip(),
    })
    return jsonify(STUDENTS[index])


@app.route("/api/admin/students/<student_id>", methods=["DELETE"])
@role_required("admin")
def api_admin_delete_student(student_id):
    index = find_student_index(student_id)
    if index is None:
        return jsonify({"error": "Student not found"}), 404
    deleted = STUDENTS.pop(index)
    return jsonify(deleted)


@app.route("/api/admin/staff")
@role_required("admin")
def api_admin_staff():
    return jsonify(STAFF_MEMBERS)


@app.route("/api/admin/staff", methods=["POST"])
@role_required("admin")
def api_admin_create_staff():
    data = request.get_json(silent=True) or {}
    staff_id = (data.get("id") or "").strip().upper()
    if not staff_id:
        return jsonify({"error": "Staff ID is required"}), 400
    if find_staff_index(staff_id) is not None:
        return jsonify({"error": "Staff ID already exists"}), 400

    staff = {
        "id": staff_id,
        "name": data.get("name", "").strip(),
        "email": data.get("email", "").strip(),
        "phone": data.get("phone", "").strip(),
        "department": data.get("department", "").strip(),
        "course_assignments": data.get("course_assignments", []),
        "role": data.get("role", "Staff").strip(),
        "profile_image": data.get("profile_image", "").strip(),
        "address": data.get("address", "").strip(),
        "status": data.get("status", "Active").strip(),
    }
    STAFF_MEMBERS.append(staff)
    return jsonify(staff), 201


@app.route("/api/admin/staff/<staff_id>", methods=["PUT"])
@role_required("admin")
def api_admin_update_staff(staff_id):
    index = find_staff_index(staff_id)
    if index is None:
        return jsonify({"error": "Staff not found"}), 404

    data = request.get_json(silent=True) or {}
    STAFF_MEMBERS[index].update({
        "name": data.get("name", STAFF_MEMBERS[index]["name"]).strip(),
        "email": data.get("email", STAFF_MEMBERS[index]["email"]).strip(),
        "phone": data.get("phone", STAFF_MEMBERS[index]["phone"]).strip(),
        "department": data.get("department", STAFF_MEMBERS[index]["department"]).strip(),
        "course_assignments": data.get("course_assignments", STAFF_MEMBERS[index]["course_assignments"]),
        "role": data.get("role", STAFF_MEMBERS[index]["role"]).strip(),
        "profile_image": data.get("profile_image", STAFF_MEMBERS[index]["profile_image"]).strip(),
        "address": data.get("address", STAFF_MEMBERS[index]["address"]).strip(),
        "status": data.get("status", STAFF_MEMBERS[index]["status"]).strip(),
    })
    return jsonify(STAFF_MEMBERS[index])


@app.route("/api/admin/staff/<staff_id>", methods=["DELETE"])
@role_required("admin")
def api_admin_delete_staff(staff_id):
    index = find_staff_index(staff_id)
    if index is None:
        return jsonify({"error": "Staff not found"}), 404
    deleted = STAFF_MEMBERS.pop(index)
    return jsonify(deleted)


@app.route("/api/admin/departments")
@role_required("admin")
def api_admin_departments():
    return jsonify(DEPARTMENTS)


@app.route("/api/admin/departments", methods=["POST"])
@role_required("admin")
def api_admin_create_department():
    data = request.get_json(silent=True) or {}
    dept_id = (data.get("id") or "").strip().upper()
    if not dept_id:
        return jsonify({"error": "Department ID is required"}), 400
    if find_department_index(dept_id) is not None:
        return jsonify({"error": "Department already exists"}), 400

    department = {
        "id": dept_id,
        "name": data.get("name", "").strip(),
        "hod": data.get("hod", "").strip(),
        "active": bool(data.get("active", True)),
        "student_count": int(data.get("student_count", 0)),
        "staff_count": int(data.get("staff_count", 0)),
    }
    DEPARTMENTS.append(department)
    return jsonify(department), 201


@app.route("/api/admin/departments/<department_id>", methods=["PUT"])
@role_required("admin")
def api_admin_update_department(department_id):
    index = find_department_index(department_id)
    if index is None:
        return jsonify({"error": "Department not found"}), 404

    data = request.get_json(silent=True) or {}
    DEPARTMENTS[index].update({
        "name": data.get("name", DEPARTMENTS[index]["name"]).strip(),
        "hod": data.get("hod", DEPARTMENTS[index]["hod"]).strip(),
        "active": bool(data.get("active", DEPARTMENTS[index]["active"])),
        "student_count": int(data.get("student_count", DEPARTMENTS[index]["student_count"])),
        "staff_count": int(data.get("staff_count", DEPARTMENTS[index]["staff_count"])),
    })
    return jsonify(DEPARTMENTS[index])


@app.route("/api/admin/departments/<department_id>", methods=["DELETE"])
@role_required("admin")
def api_admin_delete_department(department_id):
    index = find_department_index(department_id)
    if index is None:
        return jsonify({"error": "Department not found"}), 404
    deleted = DEPARTMENTS.pop(index)
    return jsonify(deleted)


@app.route("/api/admin/attendance")
@role_required("admin")
def api_admin_attendance():
    return jsonify({
        "courses": COURSES,
        "students": STUDENTS,
        "records": ATTENDANCE_RECORDS,
    })


@app.route("/api/admin/attendance", methods=["POST"])
@role_required("admin")
def api_admin_save_attendance():
    data = request.get_json(silent=True) or {}
    course_code = (data.get("course_code") or "").strip().upper()
    date_str = (data.get("date") or str(date.today())).strip()
    attendance = data.get("attendance", [])
    if not course_code or not attendance:
        return jsonify({"error": "Course code and attendance records are required"}), 400

    course = next((c for c in COURSES if c["code"] == course_code), None)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    records = ATTENDANCE_RECORDS.setdefault(course_code, [])
    existing = next((record for record in records if record["date"] == date_str), None)
    payload = {"date": date_str, "attendance": attendance}
    if existing:
        existing["attendance"] = attendance
        message = "Attendance updated"
    else:
        records.append(payload)
        message = "Attendance recorded"

    return jsonify({"message": message, "record": payload})


@app.route("/api/admin/results")
@role_required("admin")
def api_admin_results():
    return jsonify({"results": RESULT_RECORDS})


@app.route("/api/admin/results", methods=["POST"])
@role_required("admin")
def api_admin_save_result():
    data = request.get_json(silent=True) or {}
    student_id = (data.get("student_id") or "").strip().upper()
    course_code = (data.get("course_code") or "").strip().upper()
    score = data.get("score")
    if not student_id or not course_code or score is None:
        return jsonify({"error": "Student, course, and score are required"}), 400

    try:
        score = float(score)
    except (TypeError, ValueError):
        return jsonify({"error": "Score must be numeric"}), 400

    grade = grade_letter(score)
    student = next((s for s in STUDENTS if s["id"] == student_id), None)
    course = next((c for c in COURSES if c["code"] == course_code), None)
    student_name = student["name"] if student else data.get("student_name", "").strip()
    course_name = course["name"] if course else data.get("course_name", "").strip()
    existing = next((item for item in RESULT_RECORDS if item["student_id"] == student_id and item["course_code"] == course_code), None)
    payload = {
        "student_id": student_id,
        "student_name": student_name,
        "course_code": course_code,
        "course_name": course_name,
        "score": score,
        "grade": grade,
        "gpa": calculate_gpa([grade]),
        "semester": data.get("semester", "Semester 2").strip(),
        "approved": bool(data.get("approved", False)),
    }
    if existing:
        existing.update(payload)
        message = "Result updated"
    else:
        RESULT_RECORDS.append(payload)
        message = "Result created"

    return jsonify({"message": message, "result": payload})


@app.route("/api/admin/results/<student_id>/<course_code>/approve", methods=["POST"])
@role_required("admin")
def api_admin_approve_result(student_id, course_code):
    result = next((item for item in RESULT_RECORDS if item["student_id"] == student_id and item["course_code"] == course_code), None)
    if not result:
        return jsonify({"error": "Result not found"}), 404
    result["approved"] = True
    return jsonify({"message": "Result approved", "result": result})


@app.route("/api/admin/fees")
@role_required("admin")
def api_admin_fees():
    total_collected = sum(item["amount"] for item in FEE_PAYMENTS)
    total_balance = sum(item["balance"] for item in FEE_PAYMENTS)
    return jsonify({
        "payments": FEE_PAYMENTS,
        "totals": {
            "collected": total_collected,
            "balance": total_balance,
        },
        "students": STUDENTS,
    })


@app.route("/api/admin/fees", methods=["POST"])
@role_required("admin")
def api_admin_add_payment():
    data = request.get_json(silent=True) or {}
    payment_id = (data.get("id") or f"PAY{len(FEE_PAYMENTS)+1:03d}").strip().upper()
    student_id = (data.get("student_id") or "").strip().upper()
    amount = data.get("amount")
    if not student_id or amount is None:
        return jsonify({"error": "Student ID and amount are required"}), 400
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return jsonify({"error": "Amount must be numeric"}), 400

    student = next((s for s in STUDENTS if s["id"] == student_id), None)
    payment = {
        "id": payment_id,
        "student_id": student_id,
        "student_name": student["name"] if student else data.get("student_name", "").strip(),
        "amount": amount,
        "date": data.get("date", str(date.today())).strip(),
        "payment_method": data.get("payment_method", "Cash").strip(),
        "status": data.get("status", "Paid").strip(),
        "balance": float(data.get("balance", 0)),
    }
    FEE_PAYMENTS.append(payment)
    return jsonify({"message": "Payment recorded", "payment": payment}), 201


@app.route("/api/admin/fees/<payment_id>", methods=["DELETE"])
@role_required("admin")
def api_admin_delete_payment(payment_id):
    index = next((i for i, item in enumerate(FEE_PAYMENTS) if item["id"] == payment_id), None)
    if index is None:
        return jsonify({"error": "Payment not found"}), 404
    deleted = FEE_PAYMENTS.pop(index)
    return jsonify(deleted)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = current_user()
    username = session["username"]

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()

        if not name or not email:
            flash("Name and email are required", "danger")
            return redirect(url_for("profile"))

        user["name"] = name
        user["email"] = email
        user["phone"] = request.form.get("phone", "").strip()
        user["department"] = request.form.get("department", "").strip()
        user["student_id"] = request.form.get("student_id", "").strip()
        user["address"] = request.form.get("address", "").strip()
        user["city"] = request.form.get("city", "").strip()

        profile_image = request.files.get("profile_image")
        if profile_image and profile_image.filename:
            if not allowed_file(profile_image.filename):
                flash("Profile photo must be a PNG, JPG, JPEG, or GIF image", "danger")
                return redirect(url_for("profile"))
            filename = secure_filename(f"{username}_{profile_image.filename}")
            profile_image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            user["profile_image"] = f"uploads/{filename}"

        session["name"] = name

        flash("Profile updated successfully", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", user=user, user_id=username)


@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    user = current_user()

    if request.method == "POST":
        old_password = request.form.get("old_password", "").strip()
        new_password = request.form.get("new_password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not all([old_password, new_password, confirm_password]):
            flash("All fields are required", "danger")
            return redirect(url_for("change_password"))

        if not check_password_hash(user["password"], old_password):
            flash("Current password is incorrect", "danger")
            return redirect(url_for("change_password"))

        if len(new_password) < 6:
            flash("New password must be at least 6 characters", "danger")
            return redirect(url_for("change_password"))

        if new_password != confirm_password:
            flash("New passwords do not match", "danger")
            return redirect(url_for("change_password"))

        user["password"] = generate_password_hash(new_password)
        flash("Password changed successfully", "success")
        return redirect(url_for("profile"))

    return render_template("change_password.html")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        flash("Password reset email is disabled in this demo.", "info")
        return redirect(url_for("login"))
    return render_template("forgot_password.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=5000)
