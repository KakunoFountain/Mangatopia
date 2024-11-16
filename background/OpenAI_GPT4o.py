import os, glob
import sys
import argparse
import numpy as np
import multiprocessing as mp
import openai
import base64
from IPython.display import Image, display, Audio, Markdown

from detectron2.utils.logger import setup_logger

from ABCNetv2.demo import demo as abcnet
from TRBA import demo as trba

openai.api_key = os.getenv("OPENAI_APIKEY")


def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


def descripting_onmtp(codnat, pic_name, onmtp_name, picn, onpn):
  imgpath = f"./ABCNetv2/demo_images/test/{pic_name[picn]}"

  inputscript = f"左端の座標を({codnat[picn][onpn][0]},{codnat[picn][onpn][1]})，\
                右端の座標を({codnat[picn][onpn][2]},{codnat[picn][onpn][3]})として表される \
              矩形に配置されるオノマトペはどのような意図で使われてる？ \
              画像全体と共に一般的な意見を説明して．"
  inputscrip = "この画像から推定できる場面設定を説明してください"
  print(f"◆◆◆imgpath = {imgpath}")
  #display(Image(imgpath))
  print(f"◆◆◆log of line 26: inputscript = {inputscript}")
  #input()

  base64_image = encode_image(imgpath)

  response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[
      {
        "role": "system",
        "content": "あなたはカジュアルな口調で話します．漫画のワンシーンから指定されたオノマトペの意義を熱弁します．"
      },
      {
        "role": "user",
        "content": [
          {"type": "text", "text": inputscript},
          {
            "type": "image_url",
            "image_url": {
              "url": f"data:image/jpeg;base64,{base64_image}"
            }
          }
        ]
      }
    ],
    max_tokens=600,
    temperature=0.7
  )

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


#this is the summerized function
def main(pic_name, onmtpnum):
  print('aaafssdfsfda')

  terminal = False
  if terminal == False:
    print('aaada')
    sys.argv = ["ABCNetv2/demo.demo.py", \
                "--config-file", "ABCNetv2/configs/eval.yaml", \
                "--input", "ABCNetv2/demo_images/test/",  "--output", "ABCNetv2/demo_results/test/", \
                "--opts", "MODEL.WEIGHTS",  "ABCNetv2/ABCNetv2.pth"]

  #openaiに渡す材料集め
  onmtp_codnat, pics_name = abcnet.main()  #type(pics_name)=list
  if terminal == False:
    sys.argv = ["OpenAI_GPT4o.py", "--picnum", pics_name.index(pic_name), "--onmtpnum", onmtpnum]

  
  mp.set_start_method("spawn", force=True)
  args, unknown = get_parser().parse_known_args()
  logger = setup_logger()
  logger.info("Arguments: " + str(args))

  #input("dghmsgidoht")
  if not ( np.isnan(args.picnum) or np.isnan(args.onmtpnum) ):
    #input('sdffsdghgs')
    """
    onmtp_codnat=[[  6, 374,  94, 460],
       [219, 230, 296, 343],
       [214, 379, 285, 445]], [[ 169,  656,  225,  737],
       [ 754,  199,  796,  237],
       [ 236,  733,  291,  810],
       [ 932,  528,  982,  613]]
    pics_name=['sample_kimetsu.jpg', 'y_63ec7ad5931e1.jpg']"""
    onmtp_name=['さんぷる']

    #実行毎にオノマトペ履歴を消去
    for filename in glob.glob(os.path.join("./ABCNetv2/demo_results/test/", "*.jpg")):
      os.remove(filename)

    #onmtp_name = trba.main(pics_name, args.picnum, args.onmtpnum)

    
    #openaiを実行
    #logger.info(f"log of line 96: pics_name[args.picnum] = {pics_name[args.picnum]}")
    openai_outputscript = descripting_onmtp(codnat=onmtp_codnat, pic_name=pics_name, onmtp_name=onmtp_name, picn=args.picnum, onpn=args.onmtpnum)

    return openai_outputscript
  
  else:
    return "ERROR"


if __name__ == "__main__":
  main()