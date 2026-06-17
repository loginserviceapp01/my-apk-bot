import telebot
from telebot import types
import requests
import os
import threading
from flask import Flask

TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Temporary storage for user inputs
user_data = {}

@app.route('/')
def home():
    return "Bot is running!"

# 1. File capture karo
@bot.message_handler(content_types=['document'])
def handle_file(message):
    user_id = message.from_user.id
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    # File save karo
    file_path = f"{user_id}.apk"
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    user_data[user_id] = {'file_path': file_path}
    bot.reply_to(message, "File mil gayi! Ab app ka naam batao (jise file download hone par dikhe):")

# 2. Naam capture karke upload karo
@bot.message_handler(func=lambda message: message.from_user.id in user_data)
def handle_name(message):
    user_id = message.from_user.id
    app_name = message.text.replace(" ", "_") + ".apk"
    file_path = user_data[user_id]['file_path']
    
    bot.reply_to(message, "Upload ho raha hai, zara ruko...")
    
    # Upload to GoFile
    files = {'file': (app_name, open(file_path, 'rb'))}
    res = requests.post("https://store1.gofile.io/uploadFile", files=files).json()
    
    if res['status'] == 'ok':
        download_page = res['data']['downloadPage']
        # GoFile ka direct link trick
        direct_link = f"{download_page.replace('gofile.io/d/', 'gofile.io/download/')}/{app_name}"
        bot.reply_to(message, f"✅ Done!\n\nDirect Link: {direct_link}")
    else:
        bot.reply_to(message, "❌ Upload fail ho gaya.")
        
    os.remove(file_path)
    del user_data[user_id]

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.polling()).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
