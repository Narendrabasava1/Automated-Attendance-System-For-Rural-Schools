from flask import Flask, render_template, request, Response
import attendance_script

app = Flask(__name__)

users = {
    "teacher1": {"pass": "@1", "subject": "Maths"},
    "teacher2": {"pass": "@2", "subject": "Science"},
    "teacher3": {"pass": "@3", "subject": "English"},
    "teacher4": {"pass": "@4", "subject": "Hindi"},
    "teacher5": {"pass": "@5", "subject": "Social"},
}

# 🔹 Login
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        if u in users and users[u]["pass"] == p:
            subject = users[u]["subject"]
            return render_template("dashboard.html", subject=subject)

        return "Wrong login"

    return render_template("login.html")


# 🔹 Dashboard → Start attendance
@app.route("/start_attendance", methods=["POST"])
def start_attendance():
    subject = request.form["subject"]
    return render_template("attendance.html", subject=subject)


# 🔹 Video stream
@app.route("/video_feed/<subject>")
def video_feed(subject):
    return Response(
        attendance_script.generate_frames(subject),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


# 🔹 Register face
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        attendance_script.register_face(name)
        attendance_script.reload_encodings()
        return render_template("register.html", msg="Face Registered!")

    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)