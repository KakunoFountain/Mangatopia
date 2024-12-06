import os, glob
import sys
import argparse
import numpy as np
import multiprocessing as mp
from openai import OpenAI
import base64
from IPython.display import Image, display, Audio, Markdown

#api_key = os.getenv("OPENAI_APIKEY")
client = OpenAI(
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

# スレッドのメッセージを確認する関数
def thread_messages(thread_id):
    msgs = client.beta.threads.messages.list(thread_id=thread_id)
    for m in msgs:
        assert m.content[0].type == "text"
    return {"role": m.role, "message": m.content[0].text.value}

#this is the summerized function
def descripting_onmtp(filepath, fileId, codnat):

    instructions = "あなたはカジュアルな口調で話します．漫画のワンシーンから指定されたオノマトペの意義を熱弁します．"
    inputscript = f"左上の座標を({codnat[0][0]},{codnat[0][1]})，\
        右下の座標を({codnat[1][0]},{codnat[0][1]})として表される \
        矩形に配置されるオノマトペはどのような意図で使われてる？ \
        画像全体と共に一般的な意見を説明して．"
    #inputscrip = "この画像から推定できる場面設定を説明してください"
    print(f"◆◆◆log of line 26: inputscript = {inputscript}")
    #input()

    # base64_image = encode_image(filepath)

    # response = client.chat.completions.create(
    #     model="gpt-4o",
    #     messages=[
    #         {
    #             "role": "system",
    #             "content": instructions
    #         },
    #         {
    #             "role": "user",
    #             "content": [
    #                 {"type": "text", "text": inputscript},
    #                 {
    #                 "type": "image_url",
    #                 "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
    #                 }
    #             ]
    #         }
    #     ],
    #     max_tokens=600,
    #     temperature=0.7
    # )


    # アシスタントの作成
    assistant_1 = client.beta.assistants.create(
        name="onmtp",
        instructions=instructions,
        model="gpt-4-turbo"

    )
    
    response = client.chat.completions.create(
       #assistant_id=assistant_1.id,
       model='gpt-4-turbo',
       messages=[
            {
                "role": "system",
                "content": instructions
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": inputscript}
                ]
            }
        ],
        max_tokens=600,
        temperature=0.7
    )

    # スレッドの作成
    thread_1 = client.beta.threads.create(
       messages=[{
        "role": "user",
        "content": "fileIdです",
        "attachments": fileId
    }]
    )

    # 実行
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_1.id,
        assistant_id=assistant_1.id,
        #instructions="create CTR report from [related files]"
    )

    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(
            thread_id=thread_1.id
        )
        print(messages)
    else:
        print(run.status)

    # スレッドの削除
    #client.beta.threads.delete(thread_1.id)

    outputscript = response.choices[0].message.content
    print(outputscript)

    return outputscript



def get_parser():
  parser = argparse.ArgumentParser()
  parser.add_argument(
      "picnum", type=int,
      help="a selected picture in the folder",
  )
  parser.add_argument(
        "onmtpnum", type=int,
        help="a selected onomatopoeia in the picture",
    )
  
  return parser



if __name__ == "__main__":
#   file = "hoge"
#   codnat = [[1,4], [5,9]]
#   main(file, codnat)
    print('nothing is existing in main')