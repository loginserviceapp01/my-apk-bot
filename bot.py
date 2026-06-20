import telebot
import os
import threading
from supabase import create_client
from flask import Flask
from telebot import types

URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")
TOKEN = os.environ.get("TOKEN")

supabase = create_client(URL, KEY)
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@bot.message_handler(content_types=['document'])
def handle_file(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    # Unique ID taaki URL alag ho
    unique_id = f"{message.message_id}"
    file_name = f"{unique_id}_{message.document.file_name}"
    
    supabase.storage.from_("apks").upload(downloaded_file, file_name)
    url = supabase.storage.from_("apks").get_public_url(file_name)
    
    # Delete Button
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("🗑️ Delete File", callback_data=f"del_{file_name}")
    markup.add(btn)
    
    bot.reply_to(message, f"✅ Link: {url}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("del_"))
def delete_file(call):
    file_to_del = call.data.split("_", 1)[1]
    supabase.storage.from_("apks").remove(file_to_del)
    bot.edit_message_text("❌ File Deleted Successfully!", call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.polling()).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
