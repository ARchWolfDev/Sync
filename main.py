from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, send_file
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import database_connection as database
import notification as nt
from database_connection import User as Auth
from mycalendar import *
import os
import files
import dashboard as dash
import export_import
import encoder

app = Flask(__name__)
Bootstrap(app)

SECRET_KEY = 'Xn2r5u8x!A%D*G-K'
UPLOAD_FOLDER = 'static/files/userfiles/'
AVATAR_FOLDER = 'static'
CSV_FOLDER = 'static/csv/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv'}

app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['AVATAR_FOLDER'] = AVATAR_FOLDER
app.config['CSV_FOLDER'] = CSV_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)

db = database
db2 = Database()
cal = Calendar()


class User(UserMixin):
    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.password = password


@login_manager.user_loader
def load_user(user_id):
    user = Auth(id=user_id)
    if user:
        return User(user.id, user.email, user.password)
    else:
        return None


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html", logged_in=current_user.is_authenticated)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        db_user = Auth(email=email)
        if db_user.validation():
            if not check_password_hash(db_user.password, password):
                flash("Password incorrect, please try again.")
                return render_template("login.html")
            else:
                user = User(db_user.id, db_user.email, db_user.password)
                login_user(user)
                return redirect(url_for("index"))
        else:
            flash("That email does not exist, please try again.")
            return render_template("login.html")
    return render_template("login.html")


@app.route("/register/", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        user = Auth(email=request.form.get("email"))
        pass1 = request.form.get("pass1")
        pass2 = request.form.get("pass2")
        if pass1 == pass2:
            user = {
                'id': user.id,
                'password': generate_password_hash(pass1)
            }
            req_type = "users"
            db2.Update(req_type, user)
            flash("Register successfully!")
            return redirect(url_for('login'))
        else:
            flash("Passwords do not match!")
            return render_template("register.html", user=user.email)
    else:
        if request.args:
            user_id = encoder.decode(request.args.get("id"))
            user = Auth(id=user_id)
            return render_template("register.html", user=user.email)
        else:
            return redirect(url_for("login"))


@app.route("/home", methods=["POST", "GET"])
@login_required
def index():
    user = Auth(id=current_user.id).info()
    doc = files.get_file()
    avatar = db2.Select("t_emp_avatar").where(id=current_user.id)[0]
    date = request.form.get('date')
    cal.select_month(date)
    # print("date selected", date)
    return render_template("index.html", db=db, db2=db2, user=user, cal=cal, file=doc, avatar=avatar,
                           logged_in=current_user.is_authenticated, active_meniu='index')


@app.route("/request/<req_type>", methods=["POST"])
@login_required
def request_type(req_type):
    form_req = request.form.items()
    dict_req = {}
    for key, value in form_req:
        dict_req[key] = value
    # print(dict_req)
    # print(req_type)
    db.Database().Insert(req_type=req_type, data=dict_req)
    nt.insert(current_user.id, req_type)
    db2.log_requests(current_user.id, req_type)
    flash("Request submitted!")
    url = request.referrer
    return redirect(url)


@app.route("/admin/<id>", methods=["GET", "POST"])
@login_required
def admin(id):
    admin_user = Auth(id=current_user.id).info()
    if admin_user['admin'] == 1 or admin_user['admin'] == 2:
        date = request.form.get('date')
        doc = files.get_file()
        dashboard = dash.Dashboard(date)
        avatar = db2.Select("t_emp_avatar").where(id=current_user.id)[0]
        return render_template(f'{id}.html', db=db, db2=db2, cal=cal, user=admin_user, file=doc, dash=dashboard,
                               avatar=avatar, nt=nt.read(), active_tab=id, active_meniu='admin')
    else:
        return redirect(url_for("index"))


@app.route("/profile/<id>", methods=["GET", "POST"])
@login_required
def profile(id):
    profile_id = id
    user_profile = Auth(id=profile_id).info()
    logged_user = Auth(id=current_user.id).info()
    doc = files.get_file()
    avatar = db2.Select("t_emp_avatar").where(id=current_user.id)[0]
    return render_template('profile.html', db=db, db2=db2, user=logged_user, cal=cal, profile=user_profile, files=doc,
                           avatar=avatar,
                           nt=nt.read())


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    name = request.args.get('name')
    profile_id = db2.Select("v_employees").where(complete_name=name)[0][0]
    user_profile = Auth(id=profile_id).info()
    logged_user = Auth(id=current_user.id).info()
    doc = files.get_file()
    avatar = db2.Select("t_emp_avatar").where(id=current_user.id)[0]
    return render_template('profile.html', db=db, db2=db2, user=logged_user, cal=cal, profile=user_profile, files=doc,
                           avatar=avatar,
                           nt=nt.read())


@app.route("/create/<item_type>", methods=["POST"])
@login_required
def create(item_type):
    if item_type == 'tasksList':
        dict_items = {
            'list_name': request.form.get('listName'),
            'tasks': request.form.getlist('taskName')
        }
        print(dict_items, item_type)
    else:
        form_items = request.form.items()
        dict_items = {}
        for key, value in form_items:
            dict_items[key] = value
        print(dict_items)
        print(item_type)
    db2.Insert(req_type=item_type, data=dict_items)
    flash("Request submitted!")
    url = request.referrer
    return redirect(url)


@app.route("/edit/<item_type>", methods=["POST"])
@login_required
def edit(item_type):
    form_items = request.form.items()
    dict_items = {}
    for key, value in form_items:
        dict_items[key] = value
    print(dict_items)
    print(item_type)
    flash_message = "Request submitted!"
    if item_type == "users":
        new_password = dict_items['new_password1']
        db_password = db2.Select("t_users").where(id=current_user.id)[0][2]
        if check_password_hash(db_password, dict_items['old_password']):
            dict_items = {
                "id": dict_items['id'],
                'password': generate_password_hash(new_password)
            }
            db.Database().Update(req_type=item_type, data=dict_items)
        else:
            flash_message = "The current password is not correct!"
    else:
        db.Database().Update(req_type=item_type, data=dict_items)
    flash(flash_message)
    url = request.referrer
    return redirect(url)


@app.route('/requests', methods=['GET', 'POST'])
@login_required
def requests():
    if request.method == 'POST':
        # Get the url from where the request is made
        url = request.referrer
        for req in request.form.items():
            class_name = request.args.get('class')
            if class_name == 'logReq':
                db2.Delete(class_name, req[0])
            else:
                db.Database().Update(class_name, data=req)
                db2.log_requests(current_user.id, class_name, data=req, admin=True)
        return redirect(url)


@app.route("/delete/<item_type>", methods=["GET", "POST"])
@login_required
def delete(item_type):
    id = request.args.get('id')
    print(item_type)
    print(id)
    db.Database().Delete(req_type=item_type, id=id)
    if item_type == "doc":
        return jsonify({"status": "success"})
    flash("Request submitted!")
    url = request.referrer
    return redirect(url)


@app.route("/select_role", methods=["POST", "GET"])
def select_role():
    if request.method == "POST":
        department_id = request.form['category_id']
        print(department_id)
        data = db.Database().Select("t_roles").where(department_id=department_id)
        print(data)
        OutputArray = []
        for row in data:
            outputObj = {
                'id': row[0],
                'name': row[1]}
            OutputArray.append(outputObj)
        print(OutputArray)
    return jsonify(OutputArray)


@app.route('/upload/<type>', methods=['GET', 'POST'])
@login_required
def upload_file(type):
    if request.method == "POST":
        print(type)
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
            if type == "avatar":
                filename = f"images/avatar/{file.filename}"

                data = {
                    'id': current_user.id,
                    'file_name': filename
                }
                db2.Update(req_type=type, data=data)
                file.save(os.path.join(app.config['AVATAR_FOLDER'], filename))
            else:
                filename = secure_filename(file.filename)
                print(filename, current_user.id)
                db_upload_data = {
                    "user_id": current_user.id,
                    "file_path": app.config['UPLOAD_FOLDER'] + current_user.id + "/",
                    "file_name": filename
                }
                user_path = app.config['UPLOAD_FOLDER'] + current_user.id
                if not os.path.exists(user_path):
                    os.makedirs(user_path)
                db2.Insert(req_type=type, data=db_upload_data)
                file.save(os.path.join(user_path, filename))

            flash('File uploaded successfully!')
            return redirect(url_for("index"))
    else:
        flash("Please login first!")
        return redirect(url_for('login'))


@app.route('/download/', methods=['GET', 'POST'])
@login_required
def download():
    fileid = request.args.get('id')
    doc_info = db2.Select("t_emp_doc").where(id=fileid)[0]
    return send_from_directory(doc_info["file_path"], doc_info["file_name"])


@app.route('/export', methods=['GET', 'POST'])
@login_required
def export_csv():
    req_type = request.form.get('export_type')
    index = request.form.get('flexRadioIndex')
    print(type(index))
    data = export_import.create_csv(req_type, req_type_index=index)
    return send_file(data)


@app.route('/import', methods=['GET', 'POST'])
@login_required
def import_csv():
    req_type = request.form.get("import_type")
    file = request.files['file']
    print(req_type, file)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['CSV_FOLDER'], filename))
        export_import.import_csv(req_type, file.filename)
    url = request.referrer
    flash('File uploaded successfully!')
    return redirect(url)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.errorhandler(401)
def unauthorized_error(error):
    flash("You are not logged in! Please login!")
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)
