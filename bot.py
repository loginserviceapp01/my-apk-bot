import telebot
import os
import uuid
import threading
from supabase import create_client
from flask import Flask
from telebot import types

# Setup
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")
TOKEN = os.environ.get("TOKEN")
supabase = create_client(URL, KEY)
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Temporary storage for file info
user_data = {}

@app.route('/')
def home():
    return "Bot is running!"

@bot.message_handler(content_types=['document'])
def ask_for_name(message):
    # File save kar lo temporary
    user_data[message.chat.id] = message.document
    bot.reply_to(message, "📂 File mili! Is APK ka naam kya rakhna hai? (Jo naam likhoge, wahi link mein dikhega)")

@bot.message_handler(func=lambda message: message.chat.id in user_data)
def upload_to_supabase(message):
    doc = user_data.pop(message.chat.id)
    custom_name = message.text.replace(" ", "_") + ".apk"
    
    # Unique ID taaki URL different ho
    random_id = uuid.uuid4().hex[:8]
    final_path = f"{random_id}_{custom_name}"
    
    bot.reply_to(message, "⏳ Uploading...")
    
    try:
        file_info = bot.get_file(doc.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        supabase.storage.from_("apks").upload(downloaded_file, final_path)
        url = supabase.storage.from_("apks").get_public_url(final_path)
        
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("🗑️ Delete File", callback_data=f"del_{final_path}")
        markup.add(btn)
        
        bot.reply_to(message, f"✅ Done!\n\n🔗 Link: {url}", reply_markup=markup)
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("del_"))
def delete_file(call):
    file_path = call.data.split("_", 1)[1]
    supabase.storage.from_("apks").remove(file_path)
    bot.edit_message_text("❌ File Deleted!", call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.polling()).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
