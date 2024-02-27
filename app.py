from flask import Flask, render_template, redirect, request, send_from_directory
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename
import os
from api import Detector

app = Flask(__name__)
app.config['UPLOAD_DIRECTORY'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB
app.config['ALLOWED_EXTENSIONS'] = ['.jpg', '.jpeg', '.png', '.gif']

@app.route('/')
def index():
  files = os.listdir(app.config['UPLOAD_DIRECTORY'])
  images = []

  for file in files:
    if os.path.splitext(file)[1].lower() in app.config['ALLOWED_EXTENSIONS']:
      images.append(file)
  
  return render_template('index.html', images=images)

@app.route('/upload', methods=['POST'])
def upload():
  try:
    file = request.files['file']

    if file:
      extension = os.path.splitext(file.filename)[1].lower()

      if extension not in app.config['ALLOWED_EXTENSIONS']:
        return 'File is not an image.'
        
      file.save(os.path.join(
        app.config['UPLOAD_DIRECTORY'],
        secure_filename(file.filename)
      ))
  
  except RequestEntityTooLarge:
    return 'File is larger than the 16MB limit.'
  
  return redirect('/')

@app.route('/serve-image/<filename>', methods=['GET'])
def serve_image(filename):
  # Initialize detector
  detector = Detector(model_name='rapid',
                      weights_path='./weights/pL1_MWHB1024_Mar11_4000.ckpt',
                      use_cuda=False)

  # A simple example to run on a single image and plt.imshow() it
  img = detector.detect_one(img_path=filename,
                      input_size=1024, conf_thres=0.3,
                      visualize=True)
  return send_from_directory(app.config['UPLOAD_DIRECTORY'], img)