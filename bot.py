import telebot
import os
import threading
from supabase import create_client
from flask import Flask

# Environment variables se details uthayega
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")
TOKEN = os.environ.get("TOKEN")

# Supabase Client
supabase = create_client(URL, KEY)
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@bot.message_handler(content_types=['document'])
def handle_file(message):
    bot.reply_to(message, "⏳ Uploading...")
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Unique name taki file overlap na ho
        file_name = f"{message.chat.id}_{message.message_id}_{message.document.file_name}"
        
        # Supabase mein upload (bucket: apks)
        supabase.storage.from_("apks").upload(
            file=downloaded_file,
            path=file_name,
            file_options={"content-type": "application/vnd.android.package-archive"}
        )
        
        url = supabase.storage.from_("apks").get_public_url(file_name)
        bot.reply_to(message, f"✅ Link Ready:\n{url}")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.polling()).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
