import random
import sqlite3
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# ==========================================
# 1. إعدادات البوت وقاعدة البيانات
# ==========================================
TOKEN = "8625803244:AAEtk_afyd-b3LPki80G1aR3-tjE9ChNuHc"
bot = telebot.TeleBot(TOKEN)
DB_NAME = "game_bot.db"

# تخزين رقم السر لكل مستخدم في الذاكرة أثناء اللعب
num_game_sessions = {}


def init_db():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            score INTEGER DEFAULT 0
        )
    """)
  conn.commit()
  conn.close()


def get_or_create_player(user_id, username):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
  player = cursor.fetchone()

  if not player:
    cursor.execute(
        "INSERT INTO players (user_id, username) VALUES (?, ?)",
        (user_id, username or "لاعب"),
    )
    conn.commit()
    cursor.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
    player = cursor.fetchone()

  conn.close()
  return player


def add_score(user_id, points):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      "UPDATE players SET score = score + ? WHERE user_id = ?",
      (points, user_id),
  )
  conn.commit()
  conn.close()


def get_top_players():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      "SELECT username, score FROM players ORDER BY score DESC LIMIT 10"
  )
  top_players = cursor.fetchall()
  conn.close()
  return top_players


def get_player_rank(user_id):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      """
        SELECT COUNT(*) + 1 FROM players 
        WHERE score > (SELECT score FROM players WHERE user_id = ?)
    """,
      (user_id,),
  )
  rank = cursor.fetchone()[0]
  conn.close()
  return rank


# ==========================================
# 2. لعبة الرقم السري (أكبر / أصغر)
# ==========================================
def start_num_game(bot, message_or_call):
  chat_id = (
      message_or_call.chat.id
      if hasattr(message_or_call, "chat")
      else message_or_call.message.chat.id
  )
  user_id = message_or_call.from_user.id
  secret_num = random.randint(1, 10)

  num_game_sessions[user_id] = {"secret": secret_num, "attempts": 0}

  markup = InlineKeyboardMarkup(row_width=5)
  buttons = [
      InlineKeyboardButton(str(i), callback_data=f"num_{i}")
      for i in range(1, 11)
  ]
  markup.add(*buttons)

  bot.send_message(
      chat_id,
      "🔢 **لعبة الرقم السري (من 1 إلى 10):**\n"
      "لقد فكرت في رقم.. خمن ما هو الرقم؟",
      parse_mode="Markdown",
      reply_markup=markup,
  )


def handle_num_guess(bot, call):
  user_id = call.from_user.id

  if user_id not in num_game_sessions:
    bot.answer_callback_query(
        call.id,
        "⚠️ انتهت هذه اللعبة، أعد بدء اللعبة من القائمة أو أكتب 'الرقم السري'!",
        show_alert=True,
    )
    return

  guessed = int(call.data.split("_")[1])
  secret = num_game_sessions[user_id]["secret"]
  num_game_sessions[user_id]["attempts"] += 1
  attempts = num_game_sessions[user_id]["attempts"]

  if guessed == secret:
    points = max(30 - (attempts * 5), 10)
    add_score(user_id, points)
    del num_game_sessions[user_id]

    msg = (
        f"🎯 **مبروك! إجابة صحيحة!**\n"
        f"الرقم السري هو: **{secret}**\n"
        f"عدد المحاولات: **{attempts}**\n"
        f"كسبت **{points}** نقطة تنضاف لسكورك!"
    )
    bot.answer_callback_query(call.id, "🎉 إجابة صحيحة!")
    bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")

  elif guessed < secret:
    bot.answer_callback_query(call.id, f"❌ اخترت {guessed}.. الرقم أكبر! ⬆️")
    bot.send_message(
        call.message.chat.id,
        f"❌ اختار **{guessed}** وكان خطأ!\n💡 **تلميح:** الرقم المطلوب"
        " **أكبر ⬆️**",
        parse_mode="Markdown",
    )

  else:
    bot.answer_callback_query(call.id, f"❌ اخترت {guessed}.. الرقم أصغر! ⬇️")
    bot.send_message(
        call.message.chat.id,
        f"❌ اختار **{guessed}** وكان خطأ!\n💡 **تلميح:** الرقم المطلوب"
        " **أصغر ⬇️**",
        parse_mode="Markdown",
    )


# ==========================================
# 3. لعبة حجر ورقة مقص
# ==========================================
def start_rps(bot, message_or_call):
  chat_id = (
      message_or_call.chat.id
      if hasattr(message_or_call, "chat")
      else message_or_call.message.chat.id
  )
  markup = InlineKeyboardMarkup(row_width=3)
  btn_rock = InlineKeyboardButton("🪨 حجر", callback_data="rps_rock")
  btn_paper = InlineKeyboardButton("📄 ورقة", callback_data="rps_paper")
  btn_scissors = InlineKeyboardButton("✂️ مقص", callback_data="rps_scissors")
  markup.add(btn_rock, btn_paper, btn_scissors)

  bot.send_message(
      chat_id,
      "🎮 **لعبة حجر ورقة مقص**\nاختر ضربتك:",
      parse_mode="Markdown",
      reply_markup=markup,
  )


def handle_rps_choice(bot, call):
  user_choice = call.data.split("_")[1]
  options = ["rock", "paper", "scissors"]
  bot_choice = random.choice(options)

  names = {"rock": "🪨 حجر", "paper": "📄 ورقة", "scissors": "✂️ مقص"}
  user_id = call.from_user.id

  if user_choice == bot_choice:
    result = f"🤝 **تعادل!** كليكما اخترتما {names[user_choice]}."
  elif (
      (user_choice == "rock" and bot_choice == "scissors")
      or (user_choice == "paper" and bot_choice == "rock")
      or (user_choice == "scissors" and bot_choice == "paper")
  ):
    add_score(user_id, 15)
    result = (
        f"🎉 **فزت!** اختيارك: {names[user_choice]} | اختيار البوت:"
        f" {names[bot_choice]}.\nكسبت **15 نقطة** أضيفت إلى سكورك!"
    )
  else:
    result = (
        f"❌ **خسرت!** اختيارك: {names[user_choice]} | اختيار البوت:"
        f" {names[bot_choice]}."
    )

  bot.answer_callback_query(call.id, "تمت الجولة!")
  bot.send_message(call.message.chat.id, result, parse_mode="Markdown")


# ==========================================
# 4. لعبة بره السالفة (مع نظام التصويت الكامل)
# ==========================================
WORDS_DB = {
    "أطعمة": ["بيتزا", "شاورما", "برجر", "كبسة", "فلافل"],
    "حيوانات": ["أسد", "صقر", "غزال", "دلفين", "نمر"],
    "أجهزة": ["هاتف", "حاسوب", "تلفاز", "كاميرا", "ساعة ذكية"],
}

salfah_game = {
    "active": False,
    "players": {},
    "secret_word": "",
    "topic": "",
    "imposter_id": None,
    "votes": {},
    "voting_open": False,
}


def join_salfah(bot, message_or_call, reset=False):
  is_message = hasattr(message_or_call, "chat")
  chat_id = (
      message_or_call.chat.id
      if is_message
      else message_or_call.message.chat.id
  )
  user_id = message_or_call.from_user.id
  username = message_or_call.from_user.first_name

  if reset or not salfah_game["active"]:
    salfah_game["active"] = True
    salfah_game["players"] = {}
    salfah_game["votes"] = {}
    salfah_game["voting_open"] = False

  if user_id in salfah_game["players"] and not reset:
    if not is_message:
      bot.answer_callback_query(message_or_call.id, "أنت منضم بالفعل!")
    return

  salfah_game["players"][user_id] = username
  get_or_create_player(user_id, username)

  if not is_message:
    bot.answer_callback_query(message_or_call.id, "تم انضمامك بنجاح!")

  markup = InlineKeyboardMarkup()
  markup.add(
      InlineKeyboardButton("➕ انضمام", callback_data="salfah_join"),
      InlineKeyboardButton("🚀 بدء اللعبة", callback_data="salfah_start"),
  )

  players_list = "\n".join(
      [f"• {name}" for name in salfah_game["players"].values()]
  )
  msg_text = (
      f"🤫 **لعبة بره السالفة (جديدة)**\n\nاللاعبون المنضمون"
      f" ({len(salfah_game['players'])}):\n{players_list}"
  )

  bot.send_message(
      chat_id, msg_text, parse_mode="Markdown", reply_markup=markup
  )


def start_salfah_game(bot, call):
  if len(salfah_game["players"]) < 3:
    bot.answer_callback_query(
        call.id, "⚠️ يجب أن يكون عدد اللاعبين 3 على الأقل!", show_alert=True
    )
    return

  topic = random.choice(list(WORDS_DB.keys()))
  secret_word = random.choice(WORDS_DB[topic])
  player_ids = list(salfah_game["players"].keys())
  imposter_id = random.choice(player_ids)

  salfah_game["topic"] = topic
  salfah_game["secret_word"] = secret_word
  salfah_game["imposter_id"] = imposter_id
  salfah_game["votes"] = {}
  salfah_game["voting_open"] = False

  for p_id in player_ids:
    try:
      if p_id == imposter_id:
        bot.send_message(
            p_id,
            f"🤫 **أنت بره السالفة!**\nالموضوع العام هو: **{topic}**\nحاول ألا"
            " يكتشفك أحد!",
        )
      else:
        bot.send_message(
            p_id,
            f"🤫 **السالفة:**\nالموضوع: **{topic}**\nالكلمة السرية هي:"
            f" **{secret_word}**",
        )
    except Exception:
      pass

  markup = InlineKeyboardMarkup()
  markup.add(
      InlineKeyboardButton(
          "🗳️ بدء التصويت لكشف بره السالفة", callback_data="salfah_open_vote"
      )
  )

  bot.send_message(
      call.message.chat.id,
      f"🚀 **بدأت اللعبة!**\n\nالموضوع العام هو: **{topic}**\nتم إرسال الكلمات"
      " في الخاص.\nتناقشوا فيما بينكم ثم اضغطوا على زر **بدء التصويت**!",
      parse_mode="Markdown",
      reply_markup=markup,
  )


def open_salfah_voting(bot, call):
  salfah_game["voting_open"] = True
  salfah_game["votes"] = {}

  markup = InlineKeyboardMarkup(row_width=2)
  buttons = []
  for p_id, p_name in salfah_game["players"].items():
    buttons.append(
        InlineKeyboardButton(
            f"🗳️ {p_name}", callback_data=f"salfah_vote_{p_id}"
        )
    )
  markup.add(*buttons)

  bot.send_message(
      call.message.chat.id,
      "🗳️ **مرحلة التصويت بدأت!**\nاضغط على اسم الشخص الذي تشك أنه **بره"
      " السالفة**:",
      parse_mode="Markdown",
      reply_markup=markup,
  )


def handle_salfah_vote(bot, call):
  voter_id = call.from_user.id

  if not salfah_game["voting_open"]:
    bot.answer_callback_query(call.id, "التصويت مغلق حالياً!", show_alert=True)
    return

  if voter_id not in salfah_game["players"]:
    bot.answer_callback_query(
        call.id, "أنت لست مشاركاً في هذه الجولة!", show_alert=True
    )
    return

  target_id = int(call.data.split("_")[2])

  if voter_id == target_id:
    bot.answer_callback_query(
        call.id, "لا يمكنك التصويت لنفسك!", show_alert=True
    )
    return

  salfah_game["votes"][voter_id] = target_id
  voted_name = salfah_game["players"][target_id]
  bot.answer_callback_query(call.id, f"تم تصويتك لـ {voted_name}!")

  if len(salfah_game["votes"]) == len(salfah_game["players"]):
    finish_salfah_game(bot, call.message.chat.id)


def finish_salfah_game(bot, chat_id):
  salfah_game["voting_open"] = False
  imposter_id = salfah_game["imposter_id"]
  imposter_name = salfah_game["players"][imposter_id]
  secret_word = salfah_game["secret_word"]

  vote_counts = {p_id: 0 for p_id in salfah_game["players"]}
  for target in salfah_game["votes"].values():
    vote_counts[target] += 1

  most_voted_id = max(vote_counts, key=vote_counts.get)

  result_text = "📊 **نتائج التصويت والسكورات:**\n\n"

  for p_id, count in vote_counts.items():
    p_name = salfah_game["players"][p_id]
    result_text += f"• **{p_name}**: حصل على {count} صوت/أصوات\n"

  result_text += f"\n🤫 **الشخص الذي كان بره السالفة هو:** **{imposter_name}**\n"
  result_text += f"🔑 **الكلمة السرية كانت:** **{secret_word}**\n\n"

  if most_voted_id == imposter_id:
    result_text += (
        "🎉 **نجح الأعضاء في كشف من هو بره السالفة!**\n\n🏆 **النقاط المضافة"
        " للسكور:**\n"
    )
    for v_id, target in salfah_game["votes"].items():
      if target == imposter_id:
        add_score(v_id, 30)
        result_text += f"• **{salfah_game['players'][v_id]}**: +30 نقطة\n"
  else:
    add_score(imposter_id, 50)
    result_text += (
        "😈 **نجح اللي بره السالفة في خدعة الجميع ولم يكتشفوه!**\n\n🏆 **النقاط"
        " المضافة للسكور:**\n"
    )
    result_text += f"• **{imposter_name}**: +50 نقطة\n"

  salfah_game["active"] = False

  bot.send_message(chat_id, result_text, parse_mode="Markdown")


# ==========================================
# 5. لعبة المافيا
# ==========================================
mafia_game = {"active": False, "players": {}, "phase": "lobby"}


def join_mafia(bot, message_or_call, reset=False):
  is_message = hasattr(message_or_call, "chat")
  chat_id = (
      message_or_call.chat.id
      if is_message
      else message_or_call.message.chat.id
  )
  user_id = message_or_call.from_user.id
  username = message_or_call.from_user.first_name

  if reset or not mafia_game["active"]:
    mafia_game["active"] = True
    mafia_game["players"] = {}
    mafia_game["phase"] = "lobby"

  if user_id in mafia_game["players"] and not reset:
    if not is_message:
      bot.answer_callback_query(message_or_call.id, "أنت منضم بالفعل!")
    return

  mafia_game["players"][user_id] = {
      "name": username,
      "role": "مواطن",
      "alive": True,
  }
  get_or_create_player(user_id, username)

  if not is_message:
    bot.answer_callback_query(message_or_call.id, "تم انضمامك بنجاح!")

  markup = InlineKeyboardMarkup()
  markup.add(
      InlineKeyboardButton("➕ انضمام", callback_data="mafia_join"),
      InlineKeyboardButton("🚀 بدء اللعبة", callback_data="mafia_start"),
  )

  players_list = "\n".join(
      [f"• {p['name']}" for p in mafia_game["players"].values()]
  )
  msg_text = (
      f"🕵️‍♂️ **لعبة المافيا (بدأت لعبة جديدة)**\n\nاللاعبون المنضمون"
      f" ({len(mafia_game['players'])}):\n{players_list}"
  )

  bot.send_message(
      chat_id, msg_text, parse_mode="Markdown", reply_markup=markup
  )


def start_mafia_game(bot, call):
  if len(mafia_game["players"]) < 4:
    bot.answer_callback_query(
        call.id,
        "⚠️ يجب أن يكون عدد اللاعبين 4 على الأقل لتوزيع الأدوار!",
        show_alert=True,
    )
    return

  player_ids = list(mafia_game["players"].keys())
  random.shuffle(player_ids)

  mafia_id = player_ids[0]
  doctor_id = player_ids[1]
  detective_id = player_ids[2]

  mafia_game["players"][mafia_id]["role"] = "مافيا"
  mafia_game["players"][doctor_id]["role"] = "طبيب"
  mafia_game["players"][detective_id]["role"] = "محقق"

  for p_id, p_data in mafia_game["players"].items():
    try:
      bot.send_message(
          p_id, f"🎭 **دورك في لعبة المافيا هو:** {p_data['role']}"
      )
    except Exception:
      pass

  mafia_game["phase"] = "night"

  bot.send_message(
      call.message.chat.id,
      "🌙 **خيم الليل على المدينة.. ونام الجميع!**\n\n"
      "تم إرسال الأدوار في الخاص للجميع.\n"
      "على (المافيا والطبيب والمحقق) تنفيذ أدوارهم الآن عبر الرسائل الخاصة!",
      parse_mode="Markdown",
  )


# ==========================================
# 6. المشغل الرئيسي والاستجابة للنصوص
# ==========================================
init_db()


@bot.message_handler(commands=["start", "menu"])
def send_welcome(message):
  user_id = message.from_user.id
  username = message.from_user.first_name

  player = get_or_create_player(user_id, username)

  markup = InlineKeyboardMarkup(row_width=1)

  btn_mafia = InlineKeyboardButton(
      "🕵️‍♂️ لعبة المافيا (مجموعات)", callback_data="mafia_init"
  )
  btn_salfah = InlineKeyboardButton(
      "🤫 لعبة بره السالفة (مجموعات)", callback_data="salfah_init"
  )
  btn_rps = InlineKeyboardButton(
      "✂️ حجر ورقة مقص", callback_data="game_rps"
  )
  btn_num = InlineKeyboardButton(
      "🔢 لعبة الرقم السري", callback_data="game_num"
  )
  btn_top = InlineKeyboardButton(
      "🏆 قائمة التوب (أعلى 10 لاعبين)", callback_data="show_top"
  )
  btn_profile = InlineKeyboardButton(
      "📊 ملفي الشخصي والسكور", callback_data="show_profile"
  )

  markup.add(btn_mafia, btn_salfah, btn_rps, btn_num, btn_top, btn_profile)

  welcome_text = (
      f"مرحباً بك يا **{username}** في بوت الألعاب المطور! 🎮\n\n"
      f"سكورك الحالي: **{player[2]}** نقطة.\n\n"
      f"💡 **اختصارات سريعة للمجموعات:**\n"
      f"اكتب في الشات مباشرة:\n"
      f"• `مافيا` — تبدأ لعبة مافيا جديدة من الصفر\n"
      f"• `بره السالفة` — تبدأ لعبة بره السالفة مع نظام تصويت\n"
      f"• `حجر ورقة مقص` — لعبة سريعة لبناء السكور\n"
      f"• `الرقم السري` — لعبة التخمين وبناء السكور\n"
      f"• `توب` — لعرض قائمة أعلى الترتيب والسكورات\n"
      f"• `ملفي` — لعرض سكورك وترتيبك"
  )

  bot.send_message(
      message.chat.id,
      welcome_text,
      parse_mode="Markdown",
      reply_markup=markup,
  )


# === معالج الكلمات واختصارات المجموعات ===
@bot.message_handler(func=lambda message: True)
def handle_text_shortcuts(message):
  text = message.text.strip().lower()

  if "مافيا" in text:
    join_mafia(bot, message, reset=True)

  elif "بره السالفة" in text or "بره السالفه" in text:
    join_salfah(bot, message, reset=True)

  elif "حجر ورقة مقص" in text or "حجر ورقه مقص" in text:
    start_rps(bot, message)

  elif "الرقم السري" in text or "تخمين" in text:
    start_num_game(bot, message)

  elif text == "توب" or text == "التوب":
    top_list = get_top_players()
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    top_text = "🏆 **قائمة التوب (أعلى سكور بالبوت):**\n\n"
    for idx, (name, score) in enumerate(top_list):
      medal = medals[idx] if idx < len(medals) else "👤"
      top_text += f"{medal} **{name}** — {score} نقطة\n"

    bot.send_message(message.chat.id, top_text, parse_mode="Markdown")

  elif text == "ملفي" or text == "الملف":
    player = get_or_create_player(
        message.from_user.id, message.from_user.first_name
    )
    rank = get_player_rank(message.from_user.id)
    profile_text = (
        f"👤 **الملف الشخصي للاعب:**\n"
        f"• الاسم: {player[1]}\n"
        f"• السكور الحالي: {player[2]} نقطة\n"
        f"• ترتيبك بالبوت: المركز #{rank}"
    )
    bot.send_message(message.chat.id, profile_text, parse_mode="Markdown")


# === معالج ضغطات الأزرار (Callback Queries) ===
@bot.callback_query_handler(func=lambda call: True)
def handle_clicks(call):
  user_id = call.from_user.id

  if call.data == "mafia_init":
    join_mafia(bot, call, reset=True)
  elif call.data == "mafia_join":
    join_mafia(bot, call, reset=False)
  elif call.data == "mafia_start":
    start_mafia_game(bot, call)

  elif call.data == "salfah_init":
    join_salfah(bot, call, reset=True)
  elif call.data == "salfah_join":
    join_salfah(bot, call, reset=False)
  elif call.data == "salfah_start":
    start_salfah_game(bot, call)
  elif call.data == "salfah_open_vote":
    open_salfah_voting(bot, call)
  elif call.data.startswith("salfah_vote_"):
    handle_salfah_vote(bot, call)

  elif call.data == "game_rps":
    start_rps(bot, call)
  elif call.data.startswith("rps_"):
    handle_rps_choice(bot, call)

  elif call.data == "game_num":
    start_num_game(bot, call)
  elif call.data.startswith("num_"):
    handle_num_guess(bot, call)

  elif call.data == "show_top":
    top_list = get_top_players()
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    top_text = "🏆 **قائمة التوب (أعلى سكور بالبوت):**\n\n"
    for idx, (name, score) in enumerate(top_list):
      medal = medals[idx] if idx < len(medals) else "👤"
      top_text += f"{medal} **{name}** — {score} نقطة\n"

    bot.send_message(call.message.chat.id, top_text, parse_mode="Markdown")

  elif call.data == "show_profile":
    player = get_or_create_player(user_id, call.from_user.first_name)
    rank = get_player_rank(user_id)
    profile_text = (
        f"👤 **الملف الشخصي للاعب:**\n"
        f"• الاسم: {player[1]}\n"
        f"• السكور الحالي: {player[2]} نقطة\n"
        f"• ترتيبك بالبوت: المركز #{rank}"
    )
    bot.send_message(call.message.chat.id, profile_text, parse_mode="Markdown")


print("🚀 تم تشغيل البوت المحدث بنجاح...")
bot.infinity_polling()
