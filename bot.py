import telebot
import requests
import os
import threading
from flask import Flask

TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Headers taaki server request ko block na kare
HEADERS = {'User-Agent': 'Mozilla/5.0'}

@app.route('/')
def home():
    return "Bot is running!"

@bot.message_handler(content_types=['document'])
def handle_file(message):
    bot.reply_to(message, "⏳ File process ho rahi hai...")
    
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_name = message.document.file_name
    
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    try:
        # GoFile API ka use (behtar tarike se)
        files = {'file': open(file_name, 'rb')}
        response = requests.post("https://store1.gofile.io/uploadFile", files=files, headers=HEADERS)
        
        # Check karo response khali toh nahi
        if response.status_code == 200:
            res = response.json()
            if res.get('status') == 'ok':
                download_link = res['data']['downloadPage']
                bot.reply_to(message, f"✅ Success! Direct Download:\n\n{download_link}")
            else:
                bot.reply_to(message, f"❌ Server error: {res.get('status')}")
        else:
            bot.reply_to(message, f"❌ Connection error: {response.status_code}")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Code Error: {str(e)}")
        
    if os.path.exists(file_name):
        os.remove(file_name)

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.polling()).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
