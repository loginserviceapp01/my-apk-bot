import telebot
import os
import threading
import time
import requests
from supabase import create_client
from flask import Flask
from telebot import types

# 1. Configuration
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")
TOKEN = os.environ.get("TOKEN")
# Yahan apna Render URL daal do
RENDER_URL = "YOUR_RENDER_URL_HERE" 

supabase = create_client(URL, KEY)
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- SLEEP SE BACHANE KA FUNCTION ---
def keep_alive():
    while True:
        try:
            if RENDER_URL != "YOUR_RENDER_URL_HERE":
                requests.get(RENDER_URL)
        except:
            pass
        time.sleep(300) # 5 minute

user_data = {}

@app.route('/')
def home():
    return "Bot is running!"

@bot.message_handler(content_types=['document'])
def ask_for_name(message):
    user_data[message.chat.id] = message.document
    bot.reply_to(message, "📂 File mili! APK ka naam kya rakhna hai? (Agar ye naam pehle se hai, toh purani file replace ho jayegi)")

@bot.message_handler(func=lambda message: message.chat.id in user_data)
def upload_to_supabase(message):
    doc = user_data.pop(message.chat.id)
    file_name = message.text.replace(" ", "_") + ".apk"
    
    bot.reply_to(message, "⏳ Uploading and Overwriting (if exists)...")
    
    try:
        file_info = bot.get_file(doc.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        supabase.storage.from_("apks").upload(
            path=file_name, 
            file=downloaded_file,
            file_options={"content-type": "application/vnd.android.package-archive", "upsert": "true"}
        )
        
        url = supabase.storage.from_("apks").get_public_url(file_name)
        
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("🗑️ Delete File", callback_data=f"del_{file_name}")
        markup.add(btn)
        
        bot.reply_to(message, f"✅ Done! File live hai:\n\n🔗 Link: {url}", reply_markup=markup)
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("del_"))
def delete_file(call):
    file_path = call.data.split("_", 1)[1]
    try:
        supabase.storage.from_("apks").remove(file_path)
        bot.edit_message_text("❌ File Deleted Successfully!", call.message.chat.id, call.message.message_id)
    except Exception as e:
        bot.answer_callback_query(call.id, f"Error: {e}")

if __name__ == "__main__":
    # Keep alive thread
    threading.Thread(target=keep_alive, daemon=True).start()
    # Bot polling
    threading.Thread(target=lambda: bot.polling()).start()
    # Flask app
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
