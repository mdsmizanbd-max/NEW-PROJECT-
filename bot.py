import telebot
from telebot import types
import yt_dlp
import os
import time

# আপনার বটের টোকেন
API_TOKEN = '8352242557:AAGGI7bo8vqcWrjJ7abf0LT7xwcapt_M2uE'
bot = telebot.TeleBot(API_TOKEN)

# ডাটাবেস ফাইল
DB_FILE = "stats.txt"

def get_count():
    if not os.path.exists(DB_FILE): return 0
    with open(DB_FILE, "r") as f:
        try: return int(f.read().strip())
        except: return 0

def update_count():
    count = get_count() + 1
    with open(DB_FILE, "w") as f:
        f.write(str(count))

# মেইন ড্যাশবোর্ড বাটন ফাংশন
def main_dashboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("📥 DOWNLOAD VIDEO")
    btn2 = types.KeyboardButton("📊 STATUS")
    markup.add(btn1, btn2)
    return markup

# /start দিলে ড্যাশবোর্ড আসবে
@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        "👋 স্বাগতম!\n\n"
        "আমি TikTok, FB, YouTube এবং অন্যান্য সাইটের ভিডিও ডাউনলোড করতে পারি।\n"
        "নিচের ড্যাশবোর্ড থেকে অপশন বেছে নিন।"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_dashboard())

# বাটন টেক্সট হ্যান্ডলার
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == "📥 DOWNLOAD VIDEO":
        bot.send_message(message.chat.id, "🔗 আপনার ভিডিওর লিংকটি এখানে পেস্ট করুন:")
    
    elif message.text == "📊 STATUS":
        total = get_count()
        bot.send_message(message.chat.id, f"📊 **বটের বর্তমান অবস্থা:**\n\nমোট ভিডিও ডাউনলোড হয়েছে: {total} টি ✅")
    
    elif "http" in message.text:
        # রেড লিমিট ২৫ টা প্রতি সেকেন্ডে সামলানোর জন্য বিরতি
        time.sleep(0.04) # ২৫টি রিকোয়েস্ট/সেকেন্ড হিসাব করে সামান্য বিরতি
        
        msg = bot.reply_to(message, "⏳ **PROCESSING...**")
        
        file_path = f"video_{message.chat.id}.mp4"
        ydl_opts = {
            'format': 'best',
            'outtmpl': file_path,
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([message.text])
            
            with open(file_path, 'rb') as v:
                bot.send_video(
                    message.chat.id, 
                    v, 
                    caption="✅ **Download Success**",
                    reply_to_message_id=message.message_id
                )
            
            update_count()
            bot.delete_message(message.chat.id, msg.message_id)
            
            if os.path.exists(file_path):
                os.remove(file_path)

        except Exception as e:
            bot.edit_message_text("❌ ডাউনলোড ব্যর্থ হয়েছে! লিংকটি সঠিক কিনা দেখুন।", message.chat.id, msg.message_id)
            if os.path.exists(file_path):
                os.remove(file_path)
    else:
        bot.reply_to(message, "দয়া করে নিচের বাটন ব্যবহার করুন অথবা ভিডিও লিংক দিন।", reply_markup=main_dashboard())

print("বটটি এখন সক্রিয় আছে...")
bot.infinity_polling()
