from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_bootstrap import Bootstrap
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import database_connection as database
from database_connection import User
from mycalendar import *
import os
import files

app = Flask(__name__)
Bootstrap(app)

UPLOAD_FOLDER = 'static/files/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['SECRET_KEY'] = 'Xn2r5u8x!A%D*G-K'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


db = database
cal = Calendar()


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User(email)
        if user.validation():
            if not check_password_hash(user.password, password):
                flash("Password incorrect, please try again.")
                return render_template("login.html")
            else:
                session['loggedin'] = True
                session['id'] = user.id
                session['email'] = user.email
                return redirect(url_for("index"))
        else:
            flash("That email does not exist, please try again.")
            return render_template("login.html")
    return render_template("login.html")


@app.route("/")
def index():
    if 'loggedin' in session:
        current_user = User(session.get('email')).info()
        doc = files.get_file()
        return render_template("index.html", db=db, user=current_user, cal=cal, file=doc)
    flash("Please login first!")
    return redirect(url_for('login'))


@app.route("/timeoff", methods=["GET", "POST"])
def timeoff():
    if request.method == "POST":
        timeoff_request = {
            "user": session.get('id'),
            "start": request.form["start"],
            "end": request.form["end"],
            "type": request.form["type"],
            "note": request.form["note"],
        }
        print(timeoff_request)
        db.timeoff(timeoff_request)
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(filename)
                reformed_file = files.reform_file(filename, session.get('id'))
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], reformed_file))
        flash("Request submitted!")
        return redirect(url_for("index"))


@app.route("/hr-request", methods=["GET", "POST"])
def hr_request():
    if request.method == "POST":
        request_for_hr = {
            "id": "HR_REQ",
            "user": session.get('id'),
            "title": request.form["title"],
            "type": request.form["type"],
            "note": request.form["note"],
        }
        print(request_for_hr)
        db.hr_request(request_for_hr)
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                reformed_file = files.reform_file(filename, session.get('id'))
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], reformed_file))
        flash("Request submitted!")
        return redirect(url_for("index"))


@app.route("/timesheet", methods=["GET", "POST"])
def timesheet():
    if request.method == "POST":
        tasks = db.select_all("TASKS")
        departments = db.select_all("DEPARTMENTS")
        user_info = {
            "user": session.get('id'),
            "date": request.form.get("date"),
            "current_date": f"{cal.day}/{cal.month}/{cal.year}",
            "role": request.form.get("role"),
            "department": request.form["department"],
            "project": request.form["project"]
        }
        user_department = [department[0] for department in departments if user_info['department'] == department[1]]
        tasks = {task[0]: request.form.get(f"{task[0]}") for task in tasks if task[2] == user_department[0]}
        db.timesheet(user_info)
        print(user_info, tasks, user_department)
        flash("Request submitted!")
        return redirect(url_for("index"))


@app.route("/admin/<id>", methods=["GET", "POST"])
def admin(id):
    if 'loggedin' in session:
        print(id)
        admin_user = User(session.get('email')).info()
        doc = files.get_file()
        return render_template(f'{id}.html', db=db, cal=cal, user=admin_user, file=doc)


@app.route("/profile/<int:id>", methods=["GET", "POST"])
def profile(id):
    if 'loggedin' in session:
        profile_id = id
        user_email = db.select("EMPLOYEE", "ID", profile_id)[0][3]
        user_profile = User(user_email).info()
        current_user = User(session.get('email')).info()
        doc = files.get_file()
        return render_template('profile.html', db=db, user=current_user, cal=cal, profile=user_profile, files=doc)


@app.route("/create-department", methods=["GET", "POST"])
def create_department():
    if request.method == "POST":
        id = request.args.get('id')
        department = {
            'id': request.form.get('id'),
            'name': request.form.get('name'),
            'responsible': request.form.get('responsible')
        }
        if id == 'edit':
            db.edit_department(department)
        else:
            db.create_department(department)
        flash("Request submitted!")
        return redirect(url_for('admin'))


@app.route("/create-role", methods=["GET", "POST"])
def create_role():
    if request.method == "POST":
        role = {
            'id': request.form.get('id'),
            'role': request.form.get('role'),
            'department': request.form.get('department')
        }
        print(role)
        db.create_role(role)
        flash("Request submitted!")
        return redirect(url_for('admin'))


@app.route("/create-project", methods=["GET", "POST"])
def create_project():
    if request.method == "POST":
        id = request.args.get('id')
        project = {
            'id': request.form.get('id'),
            'project': request.form.get('project'),
            'client': request.form.get('client'),
            'responsible': request.form.get('responsible')
        }
        print(id, project)
        if id == 'edit':
            db.edit_project(project)
        else:
            db.create_project(project)
        flash("Request submitted!")
        return redirect(url_for('admin'))


@app.route("/add-employee", methods=["GET", "POST"])
def add_employee():
    if request.method == "POST":
        id = request.args.get('id')
        employee = {
            'id': request.form.get('id'),
            'first': request.form.get('first'),
            'last': request.form.get('last'),
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            # 'department': request.form.get('department'),
            'role': request.form.get('role'),
            'manager': request.form.get('manager'),
            'hire-date': request.form.get('hire-date'),
            'address': request.form.get('address'),
            'phone': request.form.get('phone'),
        }
        employee['password'] = generate_password_hash(generate_password_hash(employee['password']))
        if id == 'edit':
            db.edit_employee(data=employee)
        else:
            db.add_employee(employee)
        flash("Request submitted!")
        return redirect(url_for('admin'))


@app.route("/delete", methods=["GET", "POST"])
def delete():
    id = request.args.get('id')
    table = request.args.get('table')
    print(id)
    print(table)
    db.delete(id, table)
    return redirect(url_for('admin'))


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'loggedin' in session:
        if request.method == "POST":
            # check if the post request has the file part
            if 'file' not in request.files:
                flash("No file part")
                return redirect(url_for("index"))
            file = request.files['file']
            print(file.filename)
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == "":
                flash('No selected file')
                return redirect(url_for("index"))
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(filename)
                reformed_file = files.reform_file(filename, session.get('id'))
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], reformed_file))
                flash('File uploaded successfully!')
                return redirect(url_for("index"))
    else:
        flash("Please login first!")
        return redirect(url_for('login'))


@app.route('/download/', methods=['GET', 'POST'])
def download():
    if 'loggedin' in session:
        filename = request.args.get('name')
        return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/login", methods=["GET", "POST"])
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    return render_template('login.html')


if __name__ == "__main__":
    app.run(debug=True)
