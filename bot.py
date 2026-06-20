import telebot
import os
import uuid
import threading
from supabase import create_client
from flask import Flask
from telebot import types

# 1. Configuration (Values load karna)
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")
TOKEN = os.environ.get("TOKEN")

# Debugging ke liye check: Agar variables khali hain toh error dikhaye
if not URL or not KEY or not TOKEN:
    print(f"ERROR: Variables nahi mil rahe! URL={URL}, KEY={KEY}")

# Supabase Client
supabase = create_client(URL, KEY)
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_data = {}

@app.route('/')
def home():
    return "Bot is running!"

@bot.message_handler(content_types=['document'])
def ask_for_name(message):
    user_data[message.chat.id] = message.document
    bot.reply_to(message, "📂 File mili! Is APK ka naam kya rakhna hai?")

@bot.message_handler(func=lambda message: message.chat.id in user_data)
def upload_to_supabase(message):
    doc = user_data.pop(message.chat.id)
    custom_name = message.text.replace(" ", "_") + ".apk"
    random_id = uuid.uuid4().hex[:8]
    final_path = f"{random_id}_{custom_name}"
    
    bot.reply_to(message, "⏳ Uploading...")
    
    try:
        # File download
        file_info = bot.get_file(doc.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Upload to Supabase (bucket: 'apks')
        supabase.storage.from_("apks").upload(final_path, downloaded_file)
        
        url = supabase.storage.from_("apks").get_public_url(final_path)
        
        # Delete Button
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("🗑️ Delete File", callback_data=f"del_{final_path}")
        markup.add(btn)
        
        bot.reply_to(message, f"✅ Uploaded Successfully!\n\n🔗 Link: {url}", reply_markup=markup)
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
    threading.Thread(target=lambda: bot.polling()).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
