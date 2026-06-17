import telebot
import requests
import os
import threading
from flask import Flask

# Bot setup
TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Temporary memory
user_session = {}

@app.route('/')
def home():
    return "Bot is running!"

@bot.message_handler(content_types=['document'])
def handle_file(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    file_path = f"{message.from_user.id}.apk"
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    user_session[message.from_user.id] = file_path
    bot.reply_to(message, "✅ File mil gayi. Ab APK ka naam likho:")

@bot.message_handler(func=lambda message: message.from_user.id in user_session)
def handle_name(message):
    user_id = message.from_user.id
    new_name = message.text.replace(" ", "_") + ".apk"
    file_path = user_session[user_id]
    
    bot.reply_to(message, "⏳ Uploading...")
    
    try:
        # Pixeldrain direct upload
        files = {'file': (new_name, open(file_path, 'rb'))}
        res = requests.post("https://pixeldrain.com/api/file", files=files).json()
        
        if res.get('success'):
            file_id = res['id']
            # Direct Download Link (Click karte hi download start)
            direct_link = f"https://pixeldrain.com/api/file/{file_id}?download"
            bot.reply_to(message, f"🚀 Download Link:\n\n{direct_link}")
        else:
            bot.reply_to(message, "❌ Upload fail hua.")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")
    
    if os.path.exists(file_path):
        os.remove(file_path)
    del user_session[user_id]

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.polling()).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
