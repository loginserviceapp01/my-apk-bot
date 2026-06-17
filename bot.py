import telebot
import requests
import os
import threading
from flask import Flask

TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_data = {} # User ki file aur naam temporary store karne ke liye

@app.route('/')
def home():
    return "Bot is running!"

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
    bot.reply_to(message, "✅ File mil gayi! Ab App ka naam likho (e.g., WhatsApp_Mod):")

@bot.message_handler(func=lambda message: message.from_user.id in user_data)
def handle_name(message):
    user_id = message.from_user.id
    app_name = message.text.replace(" ", "_") + ".apk"
    file_path = user_data[user_id]['file_path']
    
    bot.reply_to(message, "⏳ Upload ho raha hai, zara ruko...")
    
    try:
        # GoFile upload
        files = {'file': (app_name, open(file_path, 'rb'))}
        res = requests.post("https://store1.gofile.io/uploadFile", files=files).json()
        
        if res['status'] == 'ok':
            file_id = res['data']['fileId']
            # Direct Download Link format: https://gofile.io/download/fileId/fileName
            direct_link = f"https://gofile.io/download/{file_id}/{app_name}"
            bot.reply_to(message, f"🚀 Download Ready:\n\n{direct_link}")
        else:
            bot.reply_to(message, "❌ Upload fail ho gaya.")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")
        
    os.remove(file_path)
    del user_data[user_id]

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.polling()).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
