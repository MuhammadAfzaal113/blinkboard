from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blinkboard.db'
app.config['SECRET_KEY'] = 'Cjg1yDdnZNgbpxrSI50A3jZuh7bSlQh8'
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    bio = db.Column(db.String(75), nullable=True)
    quote = db.Column(db.String(60), nullable=True)
    website = db.Column(db.String(75), nullable=True)
    blinkboard_post = db.Column(db.String(300), nullable=True)
    profile_picture = db.Column(db.String(200), nullable=True, default='uploads/default.png')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            return redirect(url_for('profile'))
        else:
            flash('Invalid credentials')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()

        if existing_user is None:
            new_user = User(username=username, password_hash=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            flash('Username already exists')
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/profile')
def profile():
    user = User.query.first()  # Or use session-based user retrieval logic
    return render_template('profile.html', user=user)

@app.route('/update_quote', methods=['POST'])
def update_quote():
    username = request.form.get('username')
    new_quote = request.form.get('value')
    user = User.query.filter_by(username=username).first()
    if user:
        user.quote = new_quote
        db.session.commit()
        return jsonify(success=True)
    return jsonify(success=False), 400

@app.route('/update_bio', methods=['POST'])
def update_bio():
    username = request.form.get('username')
    new_bio = request.form.get('value')
    user = User.query.filter_by(username=username).first()
    if user:
        user.bio = new_bio
        db.session.commit()
        return jsonify(success=True)
    return jsonify(success=False), 400

@app.route('/update_website', methods=['POST'])
def update_website():
    username = request.form.get('username')
    new_website = request.form.get('value')
    user = User.query.filter_by(username=username).first()
    if user:
        user.website = new_website
        db.session.commit()
        return jsonify(success=True)
    return jsonify(success=False), 400

@app.route('/update_blinkboard_post', methods=['POST'])
def update_blinkboard_post():
    username = request.form.get('username')
    new_post = request.form.get('value')
    user = User.query.filter_by(username=username).first()

    if user:
        user.blinkboard_post = new_post

        # Handle the image upload
        file = request.files.get('blinkboard_image')
        if file and allowed_file(file.filename):  # Implement allowed_file function for security
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            user.blinkboard_image = filename

        db.session.commit()
        return jsonify(success=True)

    return jsonify(success=False), 400

@app.route('/upload_profile_picture', methods=['POST'])
def upload_profile_picture():
    file = request.files['profile_picture']
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(os.path.join('static', filepath))

        user = User.query.first()  # Or use session-based user retrieval logic
        user.profile_picture = filepath  # Save only the part after /static
        db.session.commit()

    return redirect(url_for('profile'))

@app.route('/upload_blinkboard_image', methods=['POST'])
def upload_blinkboard_image():
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()

    if user:
        file = request.files.get('blinkboard_image')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            user.blinkboard_image = filename
            db.session.commit()
            return jsonify(success=True)

    return jsonify(success=False), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='192.168.0.226', debug=True)
