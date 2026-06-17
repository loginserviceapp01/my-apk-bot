import telebot
import requests
import os
import threading
from flask import Flask

# Token Environment Variable se le raha hai (Render Settings mein check kar lena)
TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@bot.message_handler(content_types=['document'])
def handle_file(message):
    bot.reply_to(message, "⏳ File mil gayi! Upload kar raha hoon...")
    
    # File download karo
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_name = message.document.file_name  # Ye file ka asli naam use karega
    
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    # GoFile par upload karo
    try:
        files = {'file': open(file_name, 'rb')}
        res = requests.post("https://store1.gofile.io/uploadFile", files=files).json()
        
        if res.get('status') == 'ok':
            download_link = res['data']['downloadPage']
            bot.reply_to(message, f"✅ Done!\n\nLink: {download_link}")
        else:
            bot.reply_to(message, "❌ Upload fail ho gaya.")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")
        
    # Temporary file delete karo
    os.remove(file_name)

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.polling()).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
