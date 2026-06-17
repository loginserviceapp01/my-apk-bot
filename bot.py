import telebot
import requests
import os
import random
import threading
from flask import Flask

# Token Environment Variable se le raha hai
TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def upload_to_hosting(file_path):
    sites = ["catbox", "gofile"]
    choice = random.choice(sites)
    
    if choice == "catbox":
        files = {'fileToUpload': open(file_path, 'rb')}
        data = {'reqtype': 'fileupload'}
        res = requests.post("https://catbox.moe/user/api.php", files=files, data=data)
        return f"✅ Unique Link (Catbox): {res.text}"
    
    elif choice == "gofile":
        # GoFile automatic server selection
        server_resp = requests.get("https://api.gofile.io/getServer").json()
        server = server_resp["data"]["server"]
        files = {'file': open(file_path, 'rb')}
        res = requests.post(f"https://{server}.gofile.io/uploadFile", files=files).json()
        return f"✅ Unique Link (GoFile): {res['data']['downloadPage']}"

@bot.message_handler(content_types=['document'])
def handle_file(message):
    bot.reply_to(message, "⏳ File mil gayi! Upload kar raha hoon, zara ruko...")
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_name = message.document.file_name
    
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    link = upload_to_hosting(file_name)
    bot.reply_to(message, link)
    os.remove(file_name)

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.polling()).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
