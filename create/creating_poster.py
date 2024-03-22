import requests
import base64
from pathlib import Path
from rembg import remove
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_TOKEN = os.getenv('OPENAI_API_TOKEN')

client = OpenAI(
    api_key=OPENAI_TOKEN
)

def get_title(name):
    title = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user", 
                "content": f"Take this title: {name}, and turn it into and intriguing pinterest title in 3 words or less with an exclamation mark or a symbol that represents it (adjective, name, plushie). Dont add any other text"
            }
        ]
    )

    title = title.choices[0].message.content
    
    return(title)


def shorten_string(string):
    temp = ""
    for char in string:
        #replacing spaces for _
        if char == ' ':
            char = '_'

        #ending name once a , or a - is noticed
        if char == ',' or char == '-':
            return temp
        temp += char
    
    #if no - or , is found, return the first 25 words
    return string[:25]

def encode_image(image_path):
    with open(image_path, 'rb') as image_file:
        return (base64.b64encode(image_file.read()).decode('utf-8'))


def pinterest_info(name):

    #encode the image into byte strings
    base64_image = encode_image(f'./create/images/products/{name}.png')

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': f'Looking at this image and knowing that it is a {name}, please give me a 3-8 word title for a pinterest post. Then give me a 2 sentence description enticing someone who sees my post to buy it.'},
                    {
                        'type': 'image_url',
                        "image_url": {
                            'url': f'data:image/png;base64,{base64_image}'
                        },
                    }
                ]
            }
        ],
        max_tokens=150,
    )

    return response.choices[0].message.content


def create_image(image_url, image_name):

    print(image_name)
    
    directory = Path.cwd()
    image_path = directory / f'create/images/products/{image_name}.png'

    # Send a GET request to the image URL
    response = requests.get(image_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Open a file in binary write mode,
        with open(image_path, "wb") as file:
            # Write the content of the response (which is the image in binary form) to the file
            file.write(remove(response.content))

    else:
        print("Error with status code", response.status_code)

#creating background with designated background
def create_picture(image, background_name, title):
    #opening background image
    poster = Image.open(f"./create/images/backgrounds/{background_name}.png")

    #adding the product
    main_image = Image.open(f"./create/images/products/{image}.png")

    main_image = main_image.resize((750,750)) #resizing the image

    main_image = main_image.rotate(20) #rotate by 20 degrees

    # Posting the plush on the poster
    position_img = (100, 800)
    poster.paste(main_image, position_img, main_image if main_image.mode == "RGBA" else None)
    
    #adding the text
    font = ImageFont.truetype("./create/font/Chewy-Regular.ttf", 120)

    draw = ImageDraw.Draw(poster)

    text = title

    position_text = (50, 550)

    color = (0, 0, 0)

    draw.text(position_text, text, fill=color, font=font)

    #showing outcome
    poster.save(f"./create/images/output/{image}_poster.png")



def create_poster(fields):
    image_url = fields["Image URL"]
    name = fields["Name"]

    print("getting title...")
    title = get_title(name)
    print("title made")

    print("shortening name...")
    name = shorten_string(name)
    print("name completed")

    print('creating image...')
    create_image(image_url, name)
    print('image made!')

    background = input("What background would you like? ")

    print("creating poster...")
    create_picture(name, background, title)
    print("Poster Created!!")

    print("Generating Pinterest Title and Description...")
    print(pinterest_info(name))


