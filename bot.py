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
    bot.reply_to(message, "⏳ File process ho rahi hai, zara ruko...")
    
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_name = message.document.file_name
    
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    try:
        # File.io par upload (Har baar unique link milega)
        files = {'file': open(file_name, 'rb')}
        res = requests.post("https://file.io", files=files).json()
        
        if res.get('success'):
            direct_link = res['link']
            bot.reply_to(message, f"✅ Unique Direct Link:\n\n{direct_link}\n\n(Note: Link 1 baar download ke liye hai, jo security ke liye best hai.)")
        else:
            bot.reply_to(message, "❌ Upload fail ho gaya, server busy hai.")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")
        
    if os.path.exists(file_name):
        os.remove(file_name)

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.polling()).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
