from roboflow import Roboflow
import json
from googleapiclient.discovery import build
import telebot

# Initialize the Telegram bot
bot = telebot.TeleBot('6265997298:AAH0-dkMrrMv-EEbM8FVRgLOnjISLdv40iU')

# Roboflow prediction
rf = Roboflow(api_key="pQT62y4w4YeIy9SuRcH4")
project = rf.workspace().project("gymbro")
model = project.version(2).model

file_path = 'output.json'

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    bot.send_message(message.from_user.id, "Hello, send me a picture of gym machine")

@bot.message_handler(content_types=["photo"])
def photo(message):
    raw = message.photo[-1].file_id
    path = raw + ".png"
    file = bot.get_file(raw)
    download = bot.download_file(file.file_path)
    with open(path, 'wb') as new_file:
        new_file.write(download)

    # Roboflow prediction
    data = model.predict(path, confidence=1, overlap=30).json()
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    with open(file_path) as json_file:
        data = json.load(json_file)
    prediction_class = data["predictions"][0]["class"]
    
    # YouTube search
    # Replace "YOUR_API_KEY" with your actual API key
    api_key = "AIzaSyBp-MvtXsWJNTHbikD1-wOZ1g3qgnJTo0w"
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    search_query = "How to use " + prediction_class
    part = "id"
    
    response = youtube.search().list(
        part=part,
        q=search_query
    ).execute()
    
    video_id = response['items'][0]['id']['videoId']
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    bot.send_message(message.from_user.id, "Here is your video")
    bot.send_message(message.from_user.id, video_url)

bot.polling(none_stop=True, interval=0)