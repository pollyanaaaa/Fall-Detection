from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import detection

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'mp4'}
app.config['SECRET_KEY'] = 'fdgdfgdfggf786hfg6hfg6h7f'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('player', filename=filename))
        else:
            flash('Недопустимый формат файла. Разрешён только: mp4', 'error')
            return render_template('index.html')


@app.route('/player/<filename>')
def player(filename):
    video_path = os.path.join('static/uploads', filename)
    result_path = 'static/results'
    name = detection.detection_position(video_path, result_path).split('mp4')[0].strip('.')
    return render_template('player.html', filename=name)


@app.route('/archive')
def archive():
    return render_template('archive.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5011, debug=True)
