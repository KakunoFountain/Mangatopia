from flask import Flask, request, render_template, jsonify, redirect
import os
import json
from PIL import Image

from OpenAI_GPT4o import uploaded_image, descripting_onmtp


app = Flask(__name__)
UPLOAD_FOLDER = 'uploadpics'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#解析対象画像の情報 -> "fileId", "codnat"
data = {}

# アップロードされたファイルを保存する関数
def save_image(file):
    file_path = os.path.join(UPLOAD_FOLDER, data['fileId']+".jpg")
    im = Image.open(file)

    if ".jpg" in file.filename or ".jpeg" in file.filename:
        pass
    else:
        file_path = file_path + ".jpg"
        im = im.convert("RGB")
    im.save(file_path, "JPEG")
    
    return file_path

@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():

    """HTMLフォームから送られてきた画像ファイルを処理する"""
    jsonfile = json.loads( request.files['coordinates'].read() )
    data['codnat'] = jsonfile['codnat']
    
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['image']

    #画像がアップロードされなかった場合
    if file.filename == '':
        #指定されたfileIdに対応する画像がサーバに保存されていた場合
        if not jsonfile['fileId'] == '' and os.path.exists( os.path.join(UPLOAD_FOLDER, jsonfile['fileId']+".jpg") ):
            data['fileId'] = jsonfile['fileId']
            data['filepath'] = os.path.join(UPLOAD_FOLDER, jsonfile['fileId']+".jpg")
            return jsonify({"message": "File selected successfully", "fileId": jsonfile['fileId'], "codnat": jsonfile['codnat']}), 200
        
        else:
            return jsonify({"error": "No existing file *Please uploading your file again"}), 400

    else:
        # 画像ファイルをopenaiにアップロード
        uploaded_img = uploaded_image(file)

        # 画像ファイルを保存
        if not jsonfile['codnat'] == []:
            data['filepath'] = os.path.join(UPLOAD_FOLDER, uploaded_img.id+".jpg")
            data['fileId'] = uploaded_img.id
            filepath = save_image(file)
            return jsonify({"message": "File saved successfully", "fileId": uploaded_img.id, "codnat": jsonfile['codnat']}), 200
        else:
            return jsonify({"error": "Failed to save file"}), 400



@app.route('/chat', methods=['GET'])
def chat_with_gpt():
    """fileIdと座標を受け取り、GPTで説明を生成して返す"""
    print(data)

    # アップロードされたファイルを読み込む
    if not os.path.exists(data['filepath']):
        return jsonify({"error": "File not found"}), 404

    # GPTにリクエスト
    try:
        #outputscript = "aaa"
        outputscript = descripting_onmtp(filepath=data['filepath'], fileId=data['fileId'], codnat=data['codnat'])
    except Exception as e:
        return jsonify({"error": f"GPT request failed: {str(e)}"}), 500

    return jsonify({"explanation": outputscript}), 200


if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=False, host="0.0.0.0", port=5000)