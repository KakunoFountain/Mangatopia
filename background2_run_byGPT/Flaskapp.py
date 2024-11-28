from flask import Flask, request, render_template
import os
from PIL import Image

#from OpenAI_GPT4o import main as gpt


app = Flask(__name__)
UPLOAD_FOLDER = './uploadpics'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# アップロードされたファイルを保存する関数
def save_image(file):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    
    if ".jpg" in file_path or ".jpeg" in file_path:
        file.save(file_path)
    else:
        im = Image.open(file_path)
        im = im.convert("RGB")
        file_path = file_path + ".jpg"
        im.save(file_path)
    
    return file_path

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return 'No file part'
    file = request.files['image']
    
    if file.filename == '':
        return 'No selected file'
    
    if file:
        file_path = save_image(file)
        filename = file_path.split('/')[-1]
        onmtpnum = request.form['number']
        print("◆◆◆    Received filename:{}, onmtpnum:{}".format(filename, onmtpnum))
        #openai_outputscript = gpt(filename, onmtpnum)
        openai_outputscript = "aa"
        return f"description by GPT: {openai_outputscript}"

#openai_outputscript = gpt(im)



if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)