import os
from openai import OpenAI
import base64
from PIL import Image
import hashlib

client = OpenAI(
    api_key = os.getenv("OPENAI_APIKEY")
)

file = "default"
codnat = "default"

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

#画像からハッシュ関数生成
def img_hash(file):
    with open(file, 'rb') as f:
        md5 = hashlib.md5(f.read()).hexdigest()
        f.seek(0)
    return md5

# アップロードされたファイルを保存する関数
def save_image(file, hash, UPLOAD_FOLDER):
    filepath = os.path.join(UPLOAD_FOLDER, hash+".jpg")
    im = Image.open(file)
    
    #長辺1920px以下にリサイズ
    if im.width > 1920 or im.height > 1920:
        if im.width > im.height:
            im = im.resize(1920, im.height*1920/im.width)
        else:
            im = im.resize(im.width*1920/im.height, 1920)

    if ".jpg" in file.filename or ".jpeg" in file.filename:
        pass
    else:
        im = im.convert("RGB")
    im.save(filepath, "JPEG")
    
    return filepath

#this is the summerized function
def descripting_onmtp(filepath, fileId, codnat):

    # instructions = "あなたはカジュアルな口調で話す。漫画のワンシーンから指定されたオノマトペの意義を熱弁する。\
    #     なお入力画像の座標(x,y)の原点は最も左上にとり、右に向かってx軸、下に向かってy軸の正方向とする。"
    # inputscript = f"左上の座標を({codnat[0][0]},{codnat[0][1]})，\
    #     右下の座標を({codnat[1][0]},{codnat[1][1]})として表される \
    #     矩形に配置されるオノマトペはどんな意図で使われてる？ \
    #     一般的な意見ではなく、画像全体から詳しく説明して．"
    instructions = os.getenv("INSTRUCTIONS")
    inputscript = os.getenv("INPUTSCRIPT")

    print(f"instructions = {instructions} \ninputscript = {inputscript}")

    base64_image = encode_image(filepath)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": instructions
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": inputscript},
                    {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }
        ],
        temperature=0.7
    )

    outputscript = response.choices[0].message.content
    print(f"outputscript = {outputscript}")

    return outputscript



if __name__ == "__main__":
#   file = "hoge"
#   codnat = [[1,4], [5,9]]
#   main(file, codnat)
    print('nothing is existing in main')