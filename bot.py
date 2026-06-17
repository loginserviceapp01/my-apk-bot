import telebot
import requests
import os
import threading
from flask import Flask

TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_data = {}

@app.route('/')
def home():
    return "Bot is running!"

@bot.message_handler(content_types=['document'])
def handle_file(message):
    user_id = message.from_user.id
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    file_path = f"{user_id}.apk"
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    user_data[user_id] = {'file_path': file_path}
    bot.reply_to(message, "✅ File receive ho gayi! Ab app ka naam likho:")

@bot.message_handler(func=lambda message: message.from_user.id in user_data)
def handle_name(message):
    user_id = message.from_user.id
    app_name = message.text.replace(" ", "_") + ".apk"
    file_path = user_data[user_id]['file_path']
    
    bot.reply_to(message, "⏳ Uploading to GoFile...")
    
    try:
        # File upload
        files = {'file': (app_name, open(file_path, 'rb'))}
        response = requests.post("https://store1.gofile.io/uploadFile", files=files)
        res = response.json()
        
        if res.get('status') == 'ok':
            # Direct 'downloadPage' use kar rahe hain jo sabse stable hai
            download_link = res['data']['downloadPage']
            bot.reply_to(message, f"🚀 Success!\n\nLink: {download_link}")
        else:
            bot.reply_to(message, f"❌ Error: {res.get('status')}")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Server Error: {str(e)}")
        
    if os.path.exists(file_path):
        os.remove(file_path)
    if user_id in user_data:
        del user_data[user_id]

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.polling()).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
