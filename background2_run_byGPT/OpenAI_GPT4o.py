import os
from openai import OpenAI
import base64
from PIL import Image
import hashlib
import io

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
    md5 = hashlib.md5(file.read()).hexdigest()
    file.seek(0)
    return md5

# アップロードされたファイルを保存する関数
def save_image(file, hash, UPLOAD_FOLDER):
    filepath = os.path.join(UPLOAD_FOLDER, hash+".jpg")
    im = Image.open(file)
    
    #長辺1920px以下にリサイズ
    if im.width > 1920 or im.height > 1920:
        if im.width > im.height:
            im = im.resize( 1920, int(im.height*1920/im.width) )
        else:
            im = im.resize( int(im.width*1920/im.height), 1920 )

    if ".jpg" in file.filename or ".jpeg" in file.filename:
        pass
    else:
        im = im.convert("RGB")
    im.save(filepath, "JPEG")

    im_str = encode_image(filepath)
    
    return filepath, im_str

#this is the summerized function
def descripting_onmtp(filepath, fileId, codnat):
    
    # # Example\n\
    # ## Input\n\
    # - Manga panel: A character stands on a cliff with 'ドキドキ' written.\n\
    # ## Output\n\
    # - In this scene, the character stands on a cliff. 'Doki doki' represents a pounding heart, expressing tension, anxiety, or anticipation. The background shows a high cliff and a vast sky. The gaze is distant, and the expression is slightly tense, conveying mixed feelings of determination and unease. The character’s facial tension and forehead sweat reflect fear.\n\
    

    instructions = "# Instructions\n\
1. Onomatopoeia Explanation\n\
- Clearly explain the sound, emotion, or action represented by the onomatopoeia for non-native readers.\n\
2. Context Consideration\n\
- Provide a brief explanation of the scene based on the preceding and following story or dialogue.\n\
3. Manga Scene Description\n\
- Describe the image, background, and situation where the onomatopoeia is used.\n\
4. Character Analysis\n\
- Convey the character's emotions clearly based on their gaze and facial expressions.\n\
# Output Format\n\
- Provide a concise, single-line English explanation within 50 words.\n\
# Notes\n\
- If direct translation is difficult, use actions or situations to provide clarity.\n\
- Use visual imagery or analogies to avoid ambiguity.\n\
- The origin of the coordinates (x, y) of the input image is set at the top left, with the positive direction of the x-axis toward the right and the positive direction of the y-axis toward the bottom."   
    
    inputscript = f"Onomatopoeia whose top left coodinate is ({codnat[0][0]},{codnat[0][1]}) and bottom right coodinate is ({codnat[1][0]},{codnat[1][1]}) explained in English for non-native speakers. The explanation should consider the context, characters' gaze, and facial expressions, and be within 75 words."
    
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