import os
from openai import OpenAI
import base64

client = OpenAI(
    api_key = os.getenv("OPENAI_APIKEY")
)

file = "default"
codnat = "default"

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

#openai上に画像をアップロード
def uploaded_image(file):
   uploaded_img = client.files.create(
            file=file.stream,  #ファイルをそのまま渡す
            purpose="user_data"
        )
   return uploaded_img

#this is the summerized function
def descripting_onmtp(filepath, fileId, codnat):

    instructions = "あなたはカジュアルな口調で話す。漫画のワンシーンから指定されたオノマトペの意義を熱弁する。\
        なお入力画像の座標(x,y)の原点は最も左上にとり、右に向かってx軸、下に向かってy軸の正方向とする。"
    inputscript = f"左上の座標を({codnat[0][0]},{codnat[0][1]})，\
        右下の座標を({codnat[1][0]},{codnat[1][1]})として表される \
        矩形に配置されるオノマトペはどんな意図で使われてる？ \
        一般的な意見ではなく、画像全体から詳しく説明して．"
    #inputscrip = "この画像から推定できる場面設定を説明してください"
    print(f"instructions = {instructions} \ninputscript = {inputscript}")
    #input()

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
        max_tokens=200,
        temperature=0.7
    )

    outputscript = response.choices[0].message.content
    print(outputscript)

    return outputscript



if __name__ == "__main__":
#   file = "hoge"
#   codnat = [[1,4], [5,9]]
#   main(file, codnat)
    print('nothing is existing in main')