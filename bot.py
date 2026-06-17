import telebot
import requests
import os
import threading
from flask import Flask

TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Naya wala GoFile function
def upload_to_hosting(file_path):
    try:
        files = {'file': open(file_path, 'rb')}
        res = requests.post("https://store1.gofile.io/uploadFile", files=files).json()
        if res.get('status') == 'ok':
            return f"✅ Download Link: {res['data']['downloadPage']}"
        else:
            return "❌ Upload fail ho gaya."
    except Exception as e:
        return f"❌ Error: {str(e)}"

@bot.message_handler(content_types=['document'])
def handle_file(message):
    bot.reply_to(message, "⏳ File mil gayi! Upload kar raha hoon...")
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
