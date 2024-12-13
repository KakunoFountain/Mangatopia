from flask import Flask, request, render_template, jsonify, redirect
import os
import time
import json

from OpenAI_GPT4o import img_hash, save_image, descripting_onmtp



app = Flask(__name__)
app.json.ensure_ascii = False
UPLOAD_FOLDER = 'uploadpics'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
PORT = os.getenv("PORT")

#解析対象画像の情報 -> {"fileId": , "filepath": , "codnat": , "timestamp": ,"explanation": }
data = []



@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():

    """HTMLフォームから送られてきた画像ファイルと座標を処理する"""
    jsonfile = json.loads( request.files['coordinates'].read() )
    
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['image']

    #画像ファイルを受け取らなかった場合
    if file.filename == '':
        #指定されたfileIdに対応する画像がサーバに保存されていた場合
        if not jsonfile['fileId'] == '' and os.path.exists( os.path.join(UPLOAD_FOLDER, jsonfile['fileId']+".jpg") ):
            target = next((data.index(d) for d in data if d['fileId'] == jsonfile['fileId']), None)
            if target == None:
                return jsonify({"error": "No existing file *Please uploading your file again"}), 400
            data[target]['codnat'] = jsonfile['codnat']
            return jsonify({"message": "File selected successfully", "fileId": jsonfile['fileId'], "codnat": jsonfile['codnat']}), 200
        else:
            return jsonify({"error": "No existing file *Please uploading your file again"}), 400
    #画像ファイルを受け取った場合
    else:
        # 画像ファイルを基にしたハッシュ関数を生成
        imghash = img_hash(request.files.get('image'))

        if not jsonfile['codnat'] == []:
            # loglimit分以上前の古いデータを削除
            now = time.time()
            loglimit = 30
            if data:
                while ( now - data[0]['timestamp'] >= loglimit*60 ):
                    if( os.path.isfile(data[0]['filepath']) ): os.remove(data[0]['filepath'])
                    data.pop(0)

            # 画像ファイルを保存
            filepath = save_image(file, imghash, UPLOAD_FOLDER)
            data.append({"fileId": imghash, "filepath": filepath, "codnat": jsonfile['codnat'], "timestamp": now})
            print(f"data = {data}")

            return jsonify({"message": "File saved successfully", "fileId": imghash, "codnat": jsonfile['codnat']}), 200
        else:
            return jsonify({"error": "Failed to save file"}), 400



@app.route('/chat', methods=['GET'])
def chat_with_gpt():
    """fileIdと座標を受け取り、GPTで説明を生成してfileIdに基づいた出力を返す"""

    #fileIdによるセッション識別
    queryparam = request.args.get('fileId')
    if queryparam is not None:
        target = next((data.index(d) for d in data if d['fileId'] == queryparam), None)
        if target == None:
            return jsonify({"error": "Query parameter:'fileId' not found"}), 404
    else:
        return jsonify({"error": "Query parameter:'fileId' not found"}), 404

    # アップロードされたファイルを読み込む
    if not os.path.exists(data[target]['filepath']):
        return jsonify({"error": "File not found"}), 404

    # GPTにリクエスト
    try:
        #outputscript = "aaa"
        outputscript = descripting_onmtp(filepath=data[target]['filepath'], fileId=data[target]['fileId'], codnat=data[target]['codnat'])
        data[target]['explanation'] = outputscript
    except Exception as e:
        return jsonify({"error": f"GPT request failed: {str(e)}"}), 500

    return jsonify({"explanation": outputscript}), 200


if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=False, host="0.0.0.0", port=PORT)