from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import telebot, smtplib, json, os, time

MAX_EMAILS = 6 #عدد الايميلات حط تحت 10
TOKEN = "Token"
bot = telebot.TeleBot(TOKEN)

def load_users():
    if os.path.exists('users2.json'):
        with open('users2.json', 'r') as f:
            return json.load(f)
    return []

def save_users(users):
    with open('users2.json', 'w') as f:
        json.dump(users, f, indent=4)

def load_emails():
    if os.path.exists('email.json'):
        with open('email.json', 'r') as f:
            data = json.load(f)
            for user_id in data:
                data[user_id]['email_count'] = len(data[user_id]['emails'])
            return data
    return {}

def save_emails(data):
    with open('email.json', 'w') as f:
        json.dump(data, f, indent=4)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    users = load_users()
    if str(message.from_user.id) in users or message.from_user.id == 6691026798: #ايديك
        markup = InlineKeyboardMarkup()
        add_email_button = InlineKeyboardButton("اضف ايميل", callback_data="add_email")
        send_email_button = InlineKeyboardButton("إرسال رسالة", callback_data="send_email")
        view_emails_button = InlineKeyboardButton("ايميلاتي", callback_data="show_emails")
        markup.add(add_email_button, send_email_button)
        markup.add(view_emails_button)
        bot.send_message(message.chat.id, "أهلاً بك في البوت!\n\nلاضافة ايميل اضغط اضف ايميل\nلإرسال رسالة اضغط ارسال رسالة", reply_markup=markup)
    else:bot.send_message(message.chat.id, "عذراً انت لم  تشترك بالبوت! ، للاشتراك تواصل مع @MPPPQ")

@bot.callback_query_handler(func=lambda call: call.data == "add_email")
def handle_add_email(call):
    user_credentials = load_emails()
    user_id = str(call.from_user.id)
    if user_id not in user_credentials:
        user_credentials[user_id] = {"emails": [], "email_count": 0}
    if len(user_credentials[user_id]["emails"]) >= MAX_EMAILS:
        bot.send_message(call.message.chat.id, "عذرًا، لقد وصلت الحد من الايميلات قُم بحذف واحداً على الاقل .")
        return
    bot.send_message(call.message.chat.id, "يرجى إدخال عنوان البريد الإلكتروني الخاص بك:")
    bot.register_next_step_handler(call.message, get_email)

def get_email(message):
    email = message.text
    bot.send_message(message.chat.id, "يرجى إدخال كلمة المرور الخاصة ببريدك الإلكتروني:")
    bot.register_next_step_handler(message, get_password, email)

def get_password(message, email):
    password = message.text
    user_credentials = load_emails()
    user_id = str(message.from_user.id)
    if user_id not in user_credentials:
        user_credentials[user_id] = {"emails": [], "email_count": 0}
    user_credentials[user_id]["emails"].append({"email": email, "password": password})
    user_credentials[user_id]["email_count"] = len(user_credentials[user_id]["emails"])
    save_emails(user_credentials)
    bot.send_message(message.chat.id, "تم حفظ بريدك الإلكتروني وكلمة المرور بنجاح.")

@bot.callback_query_handler(func=lambda call: call.data == "send_email")
def handle_send_email(call):
    user_credentials = load_emails()
    user_id = str(call.from_user.id)
    if user_id not in user_credentials or not user_credentials[user_id]["emails"]:
        bot.send_message(call.message.chat.id, "قم بتعيين ايميل اولاً .")
        return
    if user_credentials[user_id]['email_count'] >= MAX_EMAILS:
        bot.send_message(call.message.chat.id, "عذرًا، لقد وصلت الحد من الايميلات قُم بحذف واحداً على الاقل .")
        return
    markup = InlineKeyboardMarkup()
    for idx, email_entry in enumerate(user_credentials[user_id]["emails"]):
        markup.add(InlineKeyboardButton(email_entry["email"], callback_data=f"use_email_{idx}"))
    bot.send_message(call.message.chat.id, "اختر البريد الإلكتروني الذي تريد استخدامه لإرسال الرسالة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("use_email_"))
def handle_use_email(call):
    email_idx = int(call.data.split("_")[-1])
    bot.send_message(call.message.chat.id, "الرجاء إدخال عنوان البريد الإلكتروني الذي ترغب في إرساله إليه:")
    bot.register_next_step_handler(call.message, get_receiver_email, email_idx)

def get_receiver_email(message, email_idx):
    receiver_email = message.text
    bot.send_message(message.chat.id, "الرجاء إدخال موضوع البريد الإلكتروني:")
    bot.register_next_step_handler(message, get_email_subject, receiver_email, email_idx)

def get_email_subject(message, receiver_email, email_idx):
    subject = message.text
    bot.send_message(message.chat.id, "الرجاء إدخال محتوى البريد الإلكتروني:")
    bot.register_next_step_handler(message, get_email_content, receiver_email, subject, email_idx)

def get_email_content(message, receiver_email, subject, email_idx):
    content = message.text
    bot.send_message(message.chat.id, "كم عدد الرسائل التي تريد إرسالها :")
    bot.register_next_step_handler(message, get_email_count, receiver_email, subject, content, email_idx)

def get_email_count(message, receiver_email, subject, content, email_idx):
    try:
        email_count = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إدخال رقم صحيح.")
        return
    bot.send_message(message.chat.id, "كم مدة الاستجابة مابين الرسائل (بالثواني) :")
    bot.register_next_step_handler(message, get_email_interval, receiver_email, subject, content, email_count, email_idx)

def get_email_interval(message, receiver_email, subject, content, email_count, email_idx):
    try:
        email_interval = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إدخال رقم صحيح.")
        return
    send_final_emails(message, receiver_email, subject, content, email_count, email_interval, email_idx)

def send_final_emails(message, receiver_email, subject, content, email_count, email_interval, email_idx):
    user_credentials = load_emails()
    user_id = str(message.from_user.id)
    if user_id not in user_credentials or email_idx >= len(user_credentials[user_id]["emails"]):
        bot.send_message(message.chat.id, "حدث خطأ. يرجى المحاولة مرة أخرى.")
        return
    email_entry = user_credentials[user_id]["emails"][email_idx]
    email = email_entry['email']
    password = email_entry['password']
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email, password)
        progress_message = bot.send_message(message.chat.id, f"جاري إرسال الرسائل ..\nالرسائل حالياً : 0")
        for i in range(email_count):
            msg = MIMEMultipart()
            msg['From'] = email
            msg['To'] = receiver_email
            msg['Subject'] = subject
            msg.attach(MIMEText(content, 'plain'))
            server.send_message(msg)
            if i < email_count - 1:
                time.sleep(email_interval)
                bot.edit_message_text(chat_id=message.chat.id, message_id=progress_message.message_id, text=f"جاري إرسال الرسائل ..\nالرسائل حالياً : {i + 1}")
        server.quit()
        bot.send_message(message.chat.id, "تم إرسال البريد الإلكتروني بنجاح!")
    except Exception as e:
        bot.send_message(message.chat.id, f"فشل إرسال البريد الإلكتروني. الخطأ: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "show_emails")
def handle_show_emails(call):
    user_credentials = load_emails()
    user_id = str(call.from_user.id)
    if user_id in user_credentials and user_credentials[user_id]["emails"]:
        markup = InlineKeyboardMarkup()
        for idx, email_entry in enumerate(user_credentials[user_id]["emails"]):
            markup.add(InlineKeyboardButton(f"{email_entry['email']} 🗑️", callback_data=f"delete_email_{idx}"))
        bot.send_message(call.message.chat.id, "قائمة البريد الإلكتروني:", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "لم يتم العثور على عنوان بريد إلكتروني.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_email_"))
def handle_delete_email(call):
    email_idx = int(call.data.split("_")[-1])
    user_credentials = load_emails()
    user_id = str(call.from_user.id)
    if user_id in user_credentials and user_credentials[user_id]["emails"]:
        if email_idx < len(user_credentials[user_id]["emails"]):
            del user_credentials[user_id]["emails"][email_idx]
            user_credentials[user_id]["email_count"] = len(user_credentials[user_id]["emails"])
            save_emails(user_credentials)
            bot.send_message(call.message.chat.id, "تم حذف البريد الإلكتروني بنجاح.")
        else:
            bot.send_message(call.message.chat.id, "حدث خطأ أثناء حذف البريد الإلكتروني.")
    else:
        bot.send_message(call.message.chat.id, "لم يتم العثور على عنوان بريد إلكتروني.")

@bot.message_handler(commands=['id'])
def handle_id(message):
    if message.from_user.id == 6691026798: #ايديك
        bot.send_message(message.chat.id, "حسناً الان ارسل الايدي لتفعيله")
        bot.register_next_step_handler(message, get_user_id)

def get_user_id(message):
    user_id = message.text
    user_ids = load_users()
    if user_id not in user_ids:
        user_ids.append(user_id)
        save_users(user_ids)
        bot.send_message(message.chat.id, "تم اضافة الايدي بنجاح")
    else:bot.send_message(message.chat.id, "الايدي مضاف من قبل")

bot.polling()

# 36 186