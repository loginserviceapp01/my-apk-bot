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

@bot.message_handler(content_types=['document'])
def handle_file(message):
    bot.reply_to(message, "⏳ Uploading to fast server...")
    
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_name = message.document.file_name
    
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    try:
        # Pixeldrain API upload
        files = {'file': open(file_name, 'rb')}
        res = requests.post("https://pixeldrain.com/api/file", files=files).json()
        
        if res.get('success'):
            file_id = res['id']
            # Direct download link format
            direct_link = f"https://pixeldrain.com/api/file/{file_id}?download"
            bot.reply_to(message, f"🚀 Direct Download Link:\n\n{direct_link}")
        else:
            bot.reply_to(message, "❌ Upload fail ho gaya.")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")
        
    os.remove(file_name)

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.polling()).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
