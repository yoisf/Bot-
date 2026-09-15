import telebot
from telebot import types
import json
import os
import random
import string

# 1. ضع التوكين الخاص بك هنا
TOKEN = "8834967777:AAHXFvkmv3fAAexQNQtr7kxmUVwm_FXTBKo"
bot = telebot.TeleBot(TOKEN)

# 2. ضع معرفك والـ ID الخاص بك
ADMIN_USERNAME = "@CiCli4"
ADMIN_ID = 7816231389     # تغيير الرقم إلى ID حسابك لتعمل لوحة الأدمن

GROUP_LINK = "https://t.me/+Hxvz4UyrDONiY2My"

DATA_FILE = "members_list.json"
SENT_FILE = "sent_list.json"
CONTRIB_FILE = "contrib_list.json"
MESSAGED_FILE = "messaged_list.json"
STORE_FILE = "store_pool.json"
CODES_FILE = "vouchers.json"

def load_data(file_path, default_val):
    if not os.path.exists(file_path):
        return default_val
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default_val

def save_data(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_members(): return load_data(DATA_FILE, [])
def save_members(data): save_data(DATA_FILE, data)

def load_sent(): return load_data(SENT_FILE, [])
def save_sent(data): save_data(SENT_FILE, data)

def load_contrib(): return load_data(CONTRIB_FILE, {})
def save_contrib(data): save_data(CONTRIB_FILE, data)

def load_messaged(): return load_data(MESSAGED_FILE, {})
def save_messaged(data): save_data(MESSAGED_FILE, data)

def load_store(): return load_data(STORE_FILE, [])
def save_store(data): save_data(STORE_FILE, data)

def load_codes(): return load_data(CODES_FILE, {})
def save_codes(data): save_data(CODES_FILE, data)

def get_main_menu(user_id=None):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_start_bot  = types.KeyboardButton("🟢 ¦ بدء التشغيل (Start)")
    btn_start_dist = types.KeyboardButton("🚀 ¦ لوحة التوزيع الفاخرة")
    btn_buy_store  = types.KeyboardButton("🛒 ¦ شراء معرفات جاهزة")
    btn_redeem     = types.KeyboardButton("🔑 ¦ شحن كود شراء")
    btn_show_text  = types.KeyboardButton("📂 ¦ سلة المتبقين")
    btn_show_sent  = types.KeyboardButton("📥 ¦ سلة من تمت مراسلهم")
    btn_history    = types.KeyboardButton("📜 ¦ سجل الإنجازات والمراسلات")
    btn_top_activity = types.KeyboardButton("🏆 ¦ نشاط الأفراد (التوب)")
    btn_count      = types.KeyboardButton("📊 ¦ لوحة الإحصائيات الشاملة")
    btn_help       = types.KeyboardButton("💡 ¦ دليل الاستخدام السريع")
    
    markup.add(
        btn_start_bot, btn_start_dist, 
        btn_buy_store, btn_redeem, 
        btn_show_text, btn_show_sent, 
        btn_history, btn_top_activity, 
        btn_count, btn_help
    )

    if user_id and user_id == ADMIN_ID:
        btn_admin = types.KeyboardButton("👑 ¦ لوحة التحكم (الأدمن)")
        markup.add(btn_admin)

    return markup

@bot.message_handler(commands=['start'])
@bot.message_handler(func=lambda msg: msg.text == "🟢 ¦ بدء التشغيل (Start)")
def send_welcome(message):
    welcome_text = (
        "👑 <b>أهلاً بك في النظام الملكي المطور لإدارة وتوزيع المعرفات</b> 🤖✨\n\n"
        "🛒 <b>متجر المعرفات الجاهزة:</b> شراء معرفات حصرية تتجدد باستمرار.\n"
        "🔑 <b>نظام شحن الأكواد:</b> تفعيل المشتريات فور استلام الكود.\n"
        "🟢 <b>زر التشغيل:</b> تفعيل القائمة وإدارتها في أي وقت."
    )
    bot.reply_to(message, welcome_text, parse_mode="HTML", reply_markup=get_main_menu(message.from_user.id))

@bot.message_handler(func=lambda msg: msg.text == "👑 ¦ لوحة التحكم (الأدمن)" and msg.from_user.id == ADMIN_ID)
def admin_panel_menu(message):
    store_pool = load_store()
    codes = load_codes()
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("➕ كود 100", callback_data="adm_gen_100"),
        types.InlineKeyboardButton("➕ كود 200", callback_data="adm_gen_200"),
        types.InlineKeyboardButton("➕ كود 300", callback_data="adm_gen_300"),
        types.InlineKeyboardButton("➕ كود 400", callback_data="adm_gen_400"),
        types.InlineKeyboardButton("➕ كود 500", callback_data="adm_gen_500"),
        types.InlineKeyboardButton("➕ كود 600", callback_data="adm_gen_600")
    )
    markup.add(types.InlineKeyboardButton("📥 إضافة معرفات للمخزن", callback_data="adm_add_store"))
    
    text = (
        "👑 <b>لوحة تحكم الأدمن:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 <b>المعرفات بالمخزن:</b> <code>{len(store_pool)}</code>\n"
        f"🔑 <b>الأكواد النشطة:</b> <code>{len(codes)}</code>"
    )
    bot.reply_to(message, text, parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "🛒 ¦ شراء معرفات جاهزة")
def buy_store_menu(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📦 100 معرف — 1$", callback_data="buy_100"),
        types.InlineKeyboardButton("📦 200 معرف — 2$", callback_data="buy_200"),
        types.InlineKeyboardButton("📦 300 معرف — 3$", callback_data="buy_300"),
        types.InlineKeyboardButton("📦 400 معرف — 4$", callback_data="buy_400"),
        types.InlineKeyboardButton("📦 500 معرف — 5$", callback_data="buy_500"),
        types.InlineKeyboardButton("📦 600 معرف — 6$", callback_data="buy_600")
    )
    bot.reply_to(message, "🛒 <b>اختر الفئة المطلوبة للشراء:</b>", parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "🔑 ¦ شحن كود شراء")
def prompt_code_entry(message):
    msg = bot.reply_to(message, "🔑 <b>أدخل كود الشراء الخاص بك:</b>", parse_mode="HTML")
    bot.register_next_step_handler(msg, process_code_redemption)

def process_code_redemption(message):
    code_input = message.text.strip()
    codes = load_codes()
    if code_input in codes:
        amount = codes[code_input]
        store_pool = load_store()
        if len(store_pool) < amount:
            bot.reply_to(message, f"⚠️ المخزن يحتوي حالياً على {len(store_pool)} معرف فقط. تواصل مع الأدمن.", reply_markup=get_main_menu(message.from_user.id))
            return

        bought_items = store_pool[:amount]
        remaining_store = store_pool[amount:]
        
        members = load_members()
        sent = load_sent()
        
        added_count = 0
        for u in bought_items:
            if u not in members and u not in sent:
                members.append(u)
                added_count += 1
                
        save_members(members)
        save_store(remaining_store)
        del codes[code_input]
        save_codes(codes)
        
        bot.reply_to(message, f"🎉 <b>تم شحن الكود بنجاح!</b> أضيفت {added_count} معرفات.", parse_mode="HTML", reply_markup=get_main_menu(message.from_user.id))
    else:
        bot.reply_to(message, "❌ <b>الكود غير صحيح!</b>", parse_mode="HTML", reply_markup=get_main_menu(message.from_user.id))

def admin_process_add_store(message):
    if message.from_user.id != ADMIN_ID: return
    incoming = [w for w in message.text.split() if w.startswith('@')]
    if not incoming:
        bot.reply_to(message, "⚠️ لم يتم إدخال معرفات تبدأ بـ @.", reply_markup=get_main_menu(ADMIN_ID))
        return
    store_pool = load_store()
    added = 0
    for u in incoming:
        if u not in store_pool:
            store_pool.append(u)
            added += 1
    save_store(store_pool)
    bot.reply_to(message, f"✅ تمت إضافة <code>{added}</code> معرف للمخزن.", parse_mode="HTML", reply_markup=get_main_menu(ADMIN_ID))

@bot.message_handler(func=lambda msg: msg.text == "💡 ¦ دليل الاستخدام السريع")
def help_button(message):
    bot.reply_to(message, "💡 أرسل قائمة المعرفات مباشرة للبوت ليتم حفظها وتوزيعها.", parse_mode="HTML", reply_markup=get_main_menu(message.from_user.id))

@bot.message_handler(func=lambda msg: msg.text == "📊 ¦ لوحة الإحصائيات الشاملة")
def count_button(message):
    members, sent, store_pool = load_members(), load_sent(), load_store()
    text = (
        f"⏳ <b>المتبقون:</b> <code>{len(members)}</code>\n"
        f"✅ <b>المراسلون:</b> <code>{len(sent)}</code>\n"
        f"🛒 <b>المتجر:</b> <code>{len(store_pool)}</code>"
    )
    bot.reply_to(message, text, parse_mode="HTML", reply_markup=get_main_menu(message.from_user.id))

@bot.message_handler(func=lambda msg: msg.text == "📂 ¦ سلة المتبقين")
def show_remaining_list(message):
    members = load_members()
    if not members:
        bot.reply_to(message, "📭 السلة فارغة!", reply_markup=get_main_menu(message.from_user.id))
        return
    bot.reply_to(message, f"📂 <b>المتبقون ({len(members)}):</b>\n" + " • ".join(members), parse_mode="HTML", reply_markup=get_main_menu(message.from_user.id))

@bot.message_handler(func=lambda msg: msg.text == "📥 ¦ سلة من تمت مراسلهم")
def show_sent_list(message):
    sent = load_sent()
    if not sent:
        bot.reply_to(message, "📭 السلة فارغة!", reply_markup=get_main_menu(message.from_user.id))
        return
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🗑️ مسح الكل", callback_data="clear_sent"))
    bot.reply_to(message, f"📥 <b>المراسلون ({len(sent)}):</b>\n" + " • ".join(sent), parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "📜 ¦ سجل الإنجازات والمراسلات")
def show_history_sent(message):
    sent = load_sent()
    bot.reply_to(message, f"📜 سجل المراسلات: {len(sent)}", reply_markup=get_main_menu(message.from_user.id))

@bot.message_handler(func=lambda msg: msg.text == "🏆 ¦ نشاط الأفراد (التوب)")
def show_activity_top_menu(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📊 التوب بالمساهمات", callback_data="top_contrib"))
    bot.reply_to(message, "🏆 اختر القسم:", reply_markup=markup)

def generate_distribute_markup(members, sent_list, index):
    markup = types.InlineKeyboardMarkup(row_width=2)
    clean_username = members[index].replace('@', '')
    markup.add(types.InlineKeyboardButton(text=f"👤 مراسلة: {members[index]}", url=f"https://t.me/{clean_username}"))
    markup.add(
        types.InlineKeyboardButton(text="◀️ السابق", callback_data=f"prev_{index}"),
        types.InlineKeyboardButton(text="التالي ⏩", callback_data=f"next_{index}")
    )
    return markup

@bot.message_handler(func=lambda msg: msg.text == "🚀 ¦ لوحة التوزيع الفاخرة")
def start_distribution(message):
    members = load_members()
    sent = load_sent()
    if not members:
        bot.reply_to(message, "🎉 سلة الانتظار فارغة!", reply_markup=get_main_menu(message.from_user.id))
        return
    markup = generate_distribute_markup(members, sent, 0)
    bot.reply_to(message, f"📌 <b>العضو 1 من أصل {len(members)}:</b> <code>{members[0]}</code>", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    user_id = call.from_user.id
    
    if call.data.startswith("adm_gen_"):
        if user_id != ADMIN_ID: return
        amount = int(call.data.split("_")[2])
        code = "BUY-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        codes = load_codes()
        codes[code] = amount
        save_codes(codes)
        bot.send_message(call.message.chat.id, f"✅ <b>الكود الجديد:</b> <code>{code}</code> ({amount} معرف)", parse_mode="HTML")
        bot.answer_callback_query(call.id)
        return

    if call.data == "adm_add_store":
        msg = bot.send_message(call.message.chat.id, "📥 أرسل المعرفات للمخزن:")
        bot.register_next_step_handler(msg, admin_process_add_store)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("buy_"):
        amount = int(call.data.split("_")[1])
        bot.send_message(call.message.chat.id, f"🛍️ لطلب {amount} معرف، تواصل مع الأدمن: {ADMIN_USERNAME}")
        bot.answer_callback_query(call.id)
        return

    if call.data == "back_to_main":
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="✅ تم العودة للقائمة الرئيسية.")
        except Exception: pass
        bot.answer_callback_query(call.id)
        return

    if call.data == 'clear_sent':
        save_sent([])
        bot.answer_callback_query(call.id, "✨ تم مسح السلة")
        return

    members = load_members()
    sent = load_sent()
    if not members: return

    try:
        action, index_str = call.data.split('_')
        index = int(index_str)
    except Exception: return

    if action == 'prev':
        index = (index - 1) % len(members)
    elif action == 'next':
        # [التعديل الصحيح هنا لتلافي خطأ الفهرسة وحذف العنصر بدقة]
        current_username = members[index]
        if current_username not in sent: 
            sent.append(current_username)
        
        members.pop(index)
        save_members(members)
        save_sent(sent)
        
        if not members:
            try: 
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🎉 انتهت جميع الأسماء!")
            except Exception: pass
            bot.answer_callback_query(call.id)
            return
            
        index = index % len(members)

    markup = generate_distribute_markup(members, sent, index)
    try:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"📌 <b>العضو {index + 1} من أصل {len(members)}:</b> <code>{members[index]}</code>", parse_mode="HTML", reply_markup=markup)
    except Exception: pass
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda msg: msg.text and '@' in msg.text and not msg.text.startswith('/'))
def process_members(message):
    incoming = [w for w in message.text.split() if w.startswith('@')]
    if not incoming: return
    members, sent = load_members(), load_sent()
    added = [u for u in incoming if u not in members and u not in sent]
    if added:
        members.extend(added)
        save_members(members)
    bot.reply_to(message, f"✅ تم حفظ {len(added)} معرف جديد.", parse_mode="HTML", reply_markup=get_main_menu(message.from_user.id))

print("البوت يعمل الآن بنجاح...")
bot.infinity_polling()
