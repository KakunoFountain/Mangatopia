import os, glob
import sys
import time
import argparse
import numpy as np
import multiprocessing as mp
from openai import OpenAI
import base64
from IPython.display import Image, display, Audio, Markdown


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
            purpose="assistants"
        )
   return uploaded_img

# アシスタントが回答のメッセージを返すまで待つ関数
def wait_for_assistant_response(thread_id, run_id):
    while True:
        time.sleep(3)
        # 実行ステータスの取得
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )
        status = run.status
        if status in ["completed", "cancelled", "expired", "failed"]:
            print(status)
            break

# スレッドのメッセージを確認する関数
def thread_messages(thread_id):
    msgs = client.beta.threads.messages.list(thread_id=thread_id)
    print(msgs)
    for m in msgs:
        assert m.content[0].type == "text"
    return {"role": m.role, "message": m.content[0].text.value}



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


    # # アシスタントの作成
    # assistant_1 = client.beta.assistants.create(
    #     name="onmtp",
    #     instructions=instructions,
    #     model="gpt-4o",
    #     tools=[{"type": "code_interpreter"}]
    #     #file_ids=[fileId]
    #     # tool_resource={
    #     #    "code_interpreter": {
    #     #     "file_ids": [fileId]
    #     #    }
    #     # }
    # )
    # print("assistant_1")
    # # response = client.chat.completions.create(
    # #    assistant_id=assistant_1.id,
    # #    model='gpt-4-turbo',
    # #    messages=[
    # #         {
    # #             "role": "system",
    # #             "content": instructions
    # #         },
    # #         {
    # #             "role": "user",
    # #             "content": [
    # #                 {"type": "text", "text": inputscript}
    # #             ]
    # #         }
    # #     ],
    # #     max_tokens=600,
    # #     temperature=0.7
    # # )

    # # スレッドの作成
    # thread_1 = client.beta.threads.create(
    #     messages=[{
    #         "role": "user",
    #         "content": inputscript,
    #         #"tools": [{"type": "code_interpreter"}],
    #         "attachments": [
    #             {
    #               "tools": [{"type": "code_interpreter"}], 
    #               #"type": "image", 
    #               #"content": fileId, 
    #               "file_id": fileId
    #             }
    #         ]
    #     }]
    # )
    # print("thread_1")
    # # 実行
    # run = client.beta.threads.runs.create(
    #     thread_id=thread_1.id,
    #     assistant_id=assistant_1.id
    #     #instructions="create CTR report from [related files]"
    # )
    # print("run")
    # wait_for_assistant_response(thread_1.id,  run.id)

    # # if run.status == 'completed': 
    # #     messages = client.beta.threads.messages.list(
    # #         thread_id=thread_1.id
    # #     )
    # #     print(messages)
    # # else:
    # #     print(run.status)

    # # スレッドの削除
    # #client.beta.threads.delete(thread_1.id)
    # print("wait")

    outputscript = response.choices[0].message.content
    #outputscript = response
    #outputscript = thread_messages(thread_1.id)['message']
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