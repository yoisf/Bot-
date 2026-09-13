import telebot
from telebot import types
import json
import os

# 1. ضع التوكين الخاص بك هنا بين العلامتين
TOKEN = "8834967777:AAHXFvkmv3fAAexQNQtr7kxmUVwm_FXTBKo"
bot = telebot.TeleBot(TOKEN)

# 2. ضع رابط جروبك هنا بين العلامتين
GROUP_LINK = "https://t.me/+Hxvz4UyrDONiY2My"

DATA_FILE = "members_list.json"
SENT_FILE = "sent_list.json"
CONTRIB_FILE = "contrib_list.json" # ملف لتسجيل من ساهم بإضافة المعرفات
MESSAGED_FILE = "messaged_list.json" # ملف لتسجيل من قام بالمراسلة

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

def load_members():
    return load_data(DATA_FILE, [])

def save_members(members):
    save_data(DATA_FILE, members)

def load_sent():
    return load_data(SENT_FILE, [])

def save_sent(sent_members):
    save_data(SENT_FILE, sent_members)

def load_contrib():
    return load_data(CONTRIB_FILE, {})

def save_contrib(data):
    save_data(CONTRIB_FILE, data)

def load_messaged():
    return load_data(MESSAGED_FILE, {})

def save_messaged(data):
    save_data(MESSAGED_FILE, data)

# الأزرار الرئيسية في أسفل الشاشة
def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_start_bot  = types.KeyboardButton("🟢 ¦ بدء التشغيل (Start)")
    btn_start_dist = types.KeyboardButton("🚀 ¦ لوحة التوزيع الفاخرة")
    btn_show_text  = types.KeyboardButton("📂 ¦ سلة المتبقين")
    btn_show_sent  = types.KeyboardButton("📥 ¦ سلة من تمت مراسلهم")
    btn_history    = types.KeyboardButton("📜 ¦ سجل الإنجازات والمراسلات")
    btn_top_activity = types.KeyboardButton("🏆 ¦ نشاط الأفراد (التوب)")
    btn_count      = types.KeyboardButton("📊 ¦ لوحة الإحصائيات الشاملة")
    btn_help       = types.KeyboardButton("💡 ¦ دليل الاستخدام السريع")
    markup.add(btn_start_bot, btn_start_dist, btn_show_text, btn_show_sent, btn_history, btn_top_activity, btn_count, btn_help)
    return markup

@bot.message_handler(commands=['start'])
@bot.message_handler(func=lambda msg: msg.text == "🟢 ¦ بدء التشغيل (Start)")
def send_welcome(message):
    welcome_text = (
        "👑 <b>أهلاً بك في النظام الملكي المطور لإدارة وتوزيع المعرفات</b> 🤖✨\n\n"
        "<i>╭──────────────────────────────╮</i>\n"
        "  💎 <b>مميزات النسخة المحدثة:</b>\n"
        "<i>╰──────────────────────────────╯</i>\n"
        " 🏆 <b>لوحة نشاط الأفراد:</b> معرفة التوب للمساهمين بالمعرفات وأكثر الأشخاص مراسلة.\n"
        " 🔄 <b>مراسلة المؤرشفين:</b> إمكانية إعادة مراسلة الأشخاص في سلة من تمت مراسلهم.\n"
        " 🟢 <b>زر التشغيل (Start):</b> تفعيل وبدء التفاعل وإظهار القائمة في أي وقت.\n"
        " 🎯 <b>التنقل السريع:</b> زر (التالي) يرسل العضو تلقائياً لسلة المؤرشفين وينتقل للذي يليه."
    )
    bot.reply_to(message, welcome_text, parse_mode="HTML", reply_markup=get_main_menu())

@bot.message_handler(func=lambda msg: msg.text == "💡 ¦ دليل الاستخدام السريع")
def help_button(message):
    help_text = (
        "💡 <b>دليل التشغيل الاحترافي:</b>\n\n"
        "1️⃣ اضغط على زر <b>(🟢 ¦ بدء التشغيل)</b> لتنشيط البوت وعرض اللوحة الأساسية.\n"
        "2️⃣ أرسل لستة المعرفات (مثل <code>@user1 @user2</code>) ليحفظها البوت وتُحسب في مساهمتك.\n"
        "3️⃣ اضغط على <b>(🚀 ¦ لوحة التوزيع الفاخرة)</b> لفتح كارت العرض.\n"
        "4️⃣ يمكنك إعادة مراسلة من تمت مراسلهم سابقاً عبر زر <b>(📥 ¦ سلة من تمت مراسلهم)</b>.\n"
        "5️⃣ استخدم زر <b>(🏆 ¦ نشاط الأفراد التوب)</b> للاطلاع على ترتيب المساهمين والأكثر مراسلة."
    )
    bot.reply_to(message, help_text, parse_mode="HTML", reply_markup=get_main_menu())

@bot.message_handler(func=lambda msg: msg.text == "📊 ¦ لوحة الإحصائيات الشاملة")
def count_button(message):
    members = load_members()
    sent = load_sent()
    text = (
        "📊 <b>لوحة الإحصائيات والبيانات العامة</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⏳ <b>المتبقون في الانتظار:</b> <code>{len(members)}</code> عضو\n"
        f"✅ <b>المؤرشفون (الذين تمت مراسلهم):</b> <code>{len(sent)}</code> عضو\n"
        f"🌐 <b>إجمالي السجل الكلي:</b> <code>{len(members) + len(sent)}</code> عضو\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.reply_to(message, text, parse_mode="HTML", reply_markup=get_main_menu())

@bot.message_handler(func=lambda msg: msg.text == "📂 ¦ سلة المتبقين")
def show_remaining_list(message):
    members = load_members()
    if not members:
        bot.reply_to(message, "📭 <b>سلة المتبقين فارغة تماماً حالياً!</b>", parse_mode="HTML", reply_markup=get_main_menu())
        return
    formatted = " • ".join([f"<code>{m}</code>" for m in members])
    bot.reply_to(message, f"📂 <b>قائمة المتبقين للمراسلة ({len(members)}):</b>\n\n{formatted}", parse_mode="HTML", reply_markup=get_main_menu())

# عرض سلة من تمت مراسلهم مع إضافة زر إعادة المراسلة
@bot.message_handler(func=lambda msg: msg.text == "📥 ¦ سلة من تمت مراسلهم")
def show_sent_list(message):
    sent = load_sent()
    if not sent:
        bot.reply_to(message, "📭 <b>لا توجد أي معرفات في سلة من تمت مراسلهم حتى الآن.</b>", parse_mode="HTML", reply_markup=get_main_menu())
        return
    formatted = " • ".join([f"<code>{s}</code>" for s in sent])
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_remessage = types.InlineKeyboardButton(text="🔄 ¦ مراسلة هؤلاء الأشخاص مجدداً", callback_data="re_distribute_0")
    btn_clear = types.InlineKeyboardButton(text=f"🗑️ مسح الكل دفعة واحدة ({len(sent)})", callback_data="clear_sent")
    markup.add(btn_remessage, btn_clear)
    
    bot.reply_to(message, f"📥 <b>الأشخاص الذين تمت مراسلهم ({len(sent)}):</b>\n\n{formatted}", parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "📜 ¦ سجل الإنجازات والمراسلات")
def show_history_sent(message):
    sent = load_sent()
    if not sent:
        bot.reply_to(message, "📭 <b>السجل فارغ تماماً؛ لم تقم بمراسلة أي شخص بعد. ابدأ الآن واصنع إنجازك!</b>", parse_mode="HTML", reply_markup=get_main_menu())
        return
    
    formatted = "\n".join([f"🏆 <code>{s}</code>" for s in sent])
    history_header = (
        "🌟 <b>[ لوحة سجل الإنجازات والمراسلات الملكية ]</b> 🌟\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 <b>إجمالي الأشخاص الذين تم زيارتهم ومراسلتهم:</b> <code>{len(sent)}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{formatted}"
    )
    bot.reply_to(message, history_header, parse_mode="HTML", reply_markup=get_main_menu())

@bot.message_handler(func=lambda msg: msg.text == "🏆 ¦ نشاط الأفراد (التوب)")
def show_activity_top_menu(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_contrib = types.InlineKeyboardButton(text="📊 المساهمة بالمعرفات", callback_data="top_contrib")
    btn_messaged = types.InlineKeyboardButton(text="📩 الأكثر مراسلة", callback_data="top_messaged")
    markup.add(btn_contrib, btn_messaged)
    
    bot.reply_to(message, "🏆 <b>لوحة نشاط الأفراد (التوب):</b>\nاختر القسم الذي تريد استعراضه:", parse_mode="HTML", reply_markup=markup)

def generate_distribute_markup(members, sent_list, index):
    markup = types.InlineKeyboardMarkup(row_width=2)
    current_username = members[index]
    clean_username = current_username.replace('@', '')
    
    btn_profile = types.InlineKeyboardButton(text=f"👤 مراسلة الحساب: {current_username}", url=f"https://t.me/{clean_username}")
    markup.add(btn_profile)
    
    btn_prev = types.InlineKeyboardButton(text="◀️ السابق", callback_data=f"prev_{index}")
    btn_next = types.InlineKeyboardButton(text="التالي (تمت مراسلته) ⏩", callback_data=f"next_{index}")
    markup.add(btn_prev, btn_next)
    
    if sent_list:
        btn_clear_sent = types.InlineKeyboardButton(text=f"🗑️ مسح المؤرشفين دفعة واحدة ({len(sent_list)})", callback_data="clear_sent")
        markup.add(btn_clear_sent)
        
    return markup

# توليد لوحة خاصة لإعادة مراسلة المؤرشفين
def generate_re_distribute_markup(sent_list, index):
    markup = types.InlineKeyboardMarkup(row_width=2)
    current_username = sent_list[index]
    clean_username = current_username.replace('@', '')
    
    btn_profile = types.InlineKeyboardButton(text=f"👤 مراسلة الحساب: {current_username}", url=f"https://t.me/{clean_username}")
    markup.add(btn_profile)
    
    btn_prev = types.InlineKeyboardButton(text="◀️ السابق", callback_data=f"re_prev_{index}")
    btn_next = types.InlineKeyboardButton(text="التالي ⏩", callback_data=f"re_next_{index}")
    markup.add(btn_prev, btn_next)
    
    return markup

@bot.message_handler(commands=['list'])
@bot.message_handler(func=lambda msg: msg.text == "🚀 ¦ لوحة التوزيع الفاخرة")
def start_distribution(message):
    members = load_members()
    sent = load_sent()
    
    if not members:
        bot.reply_to(message, "🎉 <b>رائع جداً! تم الانتهاء من جميع المعرفات في سلة الانتظار.</b>\nأرسل معرفات جديدة لتبدأ من جديد.", parse_mode="HTML", reply_markup=get_main_menu())
        return
        
    index = 0
    markup = generate_distribute_markup(members, sent, index)
    
    card_text = (
        "🌟 <b>[ بطاقة العرض الذكية والتوزيع الفاخر ]</b> 🌟\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 <b>ترتيب العضو الحالي:</b> <code>{index + 1}</code> من أصل <code>{len(members)}</code>\n"
        f"👤 <b>معرف الشخص:</b> <code>{members[index]}</code>\n"
        f"📥 <b>المعزولون في السلة:</b> <code>{len(sent)}</code> عضو\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>اضغط (مراسلة الحساب) للمراسلة، ثم اضغط <b>(التالي ⏩)</b> لنقله تلقائياً لسجل المؤرشفين والانتقال لمن يليه.</i>"
    )
    bot.reply_to(message, card_text, parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    # إعادة مراسلة سلة من تمت مراسلهم
    if call.data.startswith("re_distribute_") or call.data.startswith("re_next_") or call.data.startswith("re_prev_"):
        sent = load_sent()
        if not sent:
            bot.answer_callback_query(call.id, "📭 سلة من تمت مراسلهم فارغة حالياً!", show_alert=True)
            return
            
        parts = call.data.split('_')
        action = parts[1]
        index = int(parts[2])
        
        if action == "next":
            index = (index + 1) % len(sent)
            # تسجيل نقطة للمستخدم الذي يراسل المؤرشفين أيضاً
            user = call.from_user
            user_id_str = str(user.id)
            name = user.first_name if user.first_name else (user.username if user.username else "مستخدم")
            messaged_data = load_messaged()
            if user_id_str not in messaged_data:
                messaged_data[user_id_str] = {"name": name, "count": 0}
            messaged_data[user_id_str]["name"] = name
            messaged_data[user_id_str]["count"] += 1
            save_messaged(messaged_data)
            
        elif action == "prev":
            index = (index - 1) % len(sent)
            
        markup = generate_re_distribute_markup(sent, index)
        card_text = (
            "🔄 <b>[ إعادة مراسلة سلة المؤرشفين ]</b> 🔄\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 <b>الترتيب في الأرشيف:</b> <code>{index + 1}</code> من أصل <code>{len(sent)}</code>\n"
            f"👤 <b>معرف الشخص:</b> <code>{sent[index]}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💡 <i>اضغط مراسلة الحساب، ثم اضغط <b>(التالي ⏩)</b> للانتقال للشخص التالي داخل سلة المؤرشفين.</i>"
        )
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=card_text, parse_mode="HTML", reply_markup=markup)
        except Exception:
            pass
        bot.answer_callback_query(call.id)
        return

    if call.data in ["top_contrib", "top_messaged"]:
        if call.data == "top_contrib":
            data = load_contrib()
            title = "📊 <b>أعلى 5 أشخاص ساهموا بإضافة المعرفات:</b>\n\n"
            unit = "معرف"
        else:
            data = load_messaged()
            title = "📩 <b>أعلى 5 أشخاص قاموا بالمراسلة:</b>\n\n"
            unit = "شخص راسله"

        if not data:
            bot.answer_callback_query(call.id, "📭 لا توجد بيانات مسجلة حتى الآن!", show_alert=True)
            return

        sorted_data = sorted(data.items(), key=lambda x: x[1]['count'], reverse=True)[:5]
        
        text = title
        rank = 1
        for user_id, info in sorted_data:
            medal = "🥇" if rank == 1 else ("🥈" if rank == 2 else ("🥉" if rank == 3 else f"#{rank}"))
            text += f"{medal} <b>{info['name']}</b> — <code>{info['count']}</code> {unit}\n"
            rank += 1

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="🔙 رجوع للقائمة الرئيسية", callback_data="back_to_main"))
        
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="HTML", reply_markup=markup)
        except Exception:
            pass
        bot.answer_callback_query(call.id)
        return

    if call.data == "back_to_main":
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="✅ تم العودة. استخدم الأزرار بالأسفل للتنقل.", parse_mode="HTML")
        except Exception:
            pass
        return

    members = load_members()
    sent = load_sent()

    if call.data == 'clear_sent':
        save_sent([]) 
        remaining_members = load_members()
        if not remaining_members:
            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id, 
                    message_id=call.message.message_id, 
                    text="🎉 <b>تم مسح وتصفية جميع المؤرشفين بنجاح تام! السلة أصبحت فارغة.</b>", 
                    parse_mode="HTML"
                )
            except Exception:
                pass
            return
            
        index = 0
        markup = generate_distribute_markup(remaining_members, [], index)
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"🧹 <b>تم مسح كافة المؤرشفين بنجاح!</b>\nالعضو الحالي (1 من {len(remaining_members)}):\n<code>{remaining_members[index]}</code>",
                parse_mode="HTML",
                reply_markup=markup
            )
        except Exception:
            pass
        bot.answer_callback_query(call.id, "✨ تمت تصفية السلة بنجاح", show_alert=False)
        return

    if not members:
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🎉 <b>انتهت القائمة تماماً! لا توجد أعضاء آخرين.</b>", parse_mode="HTML")
        except Exception:
            pass
        return

    try:
        action, index_str = call.data.split('_')
        index = int(index_str)
    except ValueError:
        return

    if action == 'prev':
        index = (index - 1) % len(members)

    elif action == 'next':
        if index >= len(members):
            index = len(members) - 1
            
        current_username = members[index]
        members.pop(index)
        if current_username not in sent:
            sent.append(current_username)
            
        save_members(members)
        save_sent(sent)
        
        user = call.from_user
        user_id_str = str(user.id)
        name = user.first_name if user.first_name else (user.username if user.username else "مستخدم")
        
        messaged_data = load_messaged()
        if user_id_str not in messaged_data:
            messaged_data[user_id_str] = {"name": name, "count": 0}
        messaged_data[user_id_str]["name"] = name
        messaged_data[user_id_str]["count"] += 1
        save_messaged(messaged_data)
        
        bot.answer_callback_query(call.id, f"✅ تمت مراسلة {current_username} وأرشفته", show_alert=False)
        
        if not members:
            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=(
                        "🎉 <b>أتممت مراسلة جميع الأعضاء في القائمة بنجاح مبهر!</b>\n\n"
                        f"📥 إجمالي من تمت أرشفتهم: <code>{len(sent)}</code> عضو\n\n"
                        "🏆 يمكنك تفقد زر (نشاط الأفراد التوب) من القائمة الرئيسية لمشاهدة النتائج!"
                    ),
                    parse_mode="HTML"
                )
            except Exception:
                pass
            return
            
        index = index % len(members)

    markup = generate_distribute_markup(members, sent, index)
    card_text = (
        "🌟 <b>[ بطاقة العرض الذكية والتوزيع الفاخر ]</b> 🌟\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 <b>ترتيب العضو الحالي:</b> <code>{index + 1}</code> من أصل <code>{len(members)}</code>\n"
        f"👤 <b>معرف الشخص:</b> <code>{members[index]}</code>\n"
        f"📥 <b>المعزولون في السلة:</b> <code>{len(sent)}</code> عضو\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>اضغط (مراسلة الحساب) للمراسلة، ثم اضغط <b>(التالي ⏩)</b> لنقله تلقائياً لسجل المؤرشفين والانتقال لمن يليه.</i>"
    )
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=card_text,
            parse_mode="HTML",
            reply_markup=markup
        )
    except Exception:
        pass

@bot.message_handler(func=lambda msg: msg.text and '@' in msg.text and msg.text not in ["🟢 ¦ بدء التشغيل (Start)", "🚀 ¦ لوحة التوزيع الفاخرة", "📂 ¦ سلة المتبقين", "📥 ¦ سلة من تمت مراسلهم", "📜 ¦ سجل الإنجازات والمراسلات", "🏆 ¦ نشاط الأفراد (التوب)", "📊 ¦ لوحة الإحصائيات الشاملة", "💡 ¦ دليل الاستخدام السريع"])
def process_members(message):
    words = message.text.split()
    incoming_usernames = [w for w in words if w.startswith('@')]
    
    if not incoming_usernames:
        return
        
    members = load_members()
    sent = load_sent()
    added_list = []
    
    for username in incoming_usernames:
        if username not in members and username not in sent:
            members.append(username)
            added_list.append(username)
            
    if added_list:
        save_members(members)
        
        user = message.from_user
        user_id_str = str(user.id)
        name = user.first_name if user.first_name else (user.username if user.username else "مستخدم")
        
        contrib_data = load_contrib()
        if user_id_str not in contrib_data:
            contrib_data[user_id_str] = {"name": name, "count": 0}
        contrib_data[user_id_str]["name"] = name
        contrib_data[user_id_str]["count"] += len(added_list)
        save_contrib(contrib_data)
    
    response_msg = "🛠️ <b>تقرير إضافة المعرفات الجديد:</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    if added_list:
        response_msg += f"✅ <b>تمت إضافتها بنجاح ({len(added_list)}):</b>\n" + " • ".join([f"<code>{u}</code>" for u in added_list]) + "\n\n"
    else:
        response_msg += "⚠️ المعرفات المدخلة مضافة مسبقاً أو موجودة في سجل الإنجازات.\n\n"
        
    response_msg += f"📊 <b>إجمالي المتبقين في الانتظار:</b> <code>{len(members)}</code> عضو"
    bot.reply_to(message, response_msg, parse_mode="HTML", reply_markup=get_main_menu())

print("البوت يعمل الآن بنجاح مع إضافة خاصية مراسلة المؤرشفين...")
bot.infinity_polling()
 