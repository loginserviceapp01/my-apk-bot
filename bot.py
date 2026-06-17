import telebot
import requests
import os
import threading
from flask import Flask

TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_session = {}

@app.route('/')
def home():
    return "Bot is running!"

@bot.message_handler(content_types=['document'])
def handle_file(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_path = f"{message.from_user.id}.apk"
    with open(file_path, 'wb') as f:
        f.write(downloaded_file)
    
    user_session[message.from_user.id] = file_path
    bot.reply_to(message, "✅ File mil gayi! Ab APK ka naam likho:")

@bot.message_handler(func=lambda message: message.from_user.id in user_session)
def handle_name(message):
    user_id = message.from_user.id
    file_name = message.text.replace(" ", "_") + ".apk"
    file_path = user_session[user_id]
    
    bot.reply_to(message, "⏳ Uploading to Transfer.sh...")
    
    try:
        # Transfer.sh ka use kar rahe hain (ye bahut stable hai)
        with open(file_path, 'rb') as f:
            res = requests.put(f"https://transfer.sh/{file_name}", data=f)
        
        if res.status_code == 200:
            direct_link = res.text.strip()
            bot.reply_to(message, f"🚀 Direct Download Link:\n\n{direct_link}")
        else:
            bot.reply_to(message, f"❌ Error: {res.status_code}")
    except Exception as e:
        bot.reply_to(message, f"❌ Exception: {str(e)}")
    
    if os.path.exists(file_path):
        os.remove(file_path)
    del user_session[user_id]

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.polling()).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
