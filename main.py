import os
import json
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, \
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from Tic.util import dB
from Tic.erornya import bajingan

# Load environment variables
load_dotenv()

app = Client(
    "er",
    api_id=os.getenv("API_ID"),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN")
)

# Constants
MUST_JOIN = os.getenv("MUST_JOIN", "").split(",")  # Ensure MUST_JOIN is a list
LOGS_GROUP_ID = int(os.getenv("LOGS_GROUP_ID", "0"))

CONTACT_KEYS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("📢 Support", url="t.me/er_support_group"),
        InlineKeyboardButton("👤 Owner", url="t.me/chakszzz")
    ],
    [
        InlineKeyboardButton("✉️ Email", callback_data=json.dumps({"type": "C", "action": "email"}))
    ]
])

# Helper function
def mention(name: str, id: int) -> str:
    return f"[{name}](tg://user?id={id})"

# Middleware for ensuring users join required channels
@app.on_message(filters.incoming & filters.private, group=-1)
@bajingan
def must_join_channel(app: Client, msg: Message):
    if not MUST_JOIN:
        return
    try:
        for channel in MUST_JOIN:
            try:
                app.get_chat_member(channel, msg.from_user.id)
            except UserNotParticipant:
                link = f"https://t.me/{channel}" if channel.isalpha() else app.get_chat(channel).invite_link
                app.send_message(
                    msg.chat.id,
                    f"Untuk menggunakan bot ini, kamu harus bergabung di channel kami [di sini]({link}). "
                    "Setelah bergabung, ketik /start kembali.",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("🔗 Gabung Sekarang", url=link)]]
                    )
                )
                msg.stop_propagation()
    except ChatAdminRequired:
        app.send_message(LOGS_GROUP_ID, f"Bot harus menjadi admin di {MUST_JOIN} untuk memverifikasi pengguna.")

# Command handlers
@app.on_message(filters.command("start"))
@bajingan
def start_handler(bot: Client, message: Message):
    bot.send_message(
        message.chat.id,
        f"Hi **{message.from_user.first_name}**!\n\n"
        "Untuk memulai, klik tombol **Bermain** dan pilih grup untuk bermain.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎮 Bermain", switch_inline_query=" Main")]
        ])
    )

@app.on_message(filters.command("contact"))
@bajingan
def contact_handler(bot: Client, message: Message):
    bot.send_message(
        message.chat.id,
        "Silakan hubungi kami melalui tombol di bawah ini.",
        reply_markup=CONTACT_KEYS
    )

@app.on_message(filters.command("stats"))
@bajingan
def stats_handler(bot: Client, message: Message):
    user_id = message.from_user.id
    stats = dB.get_user_stats(user_id)

    hours, remainder = divmod(stats["total_play_time"], 3600)
    minutes, seconds = divmod(remainder, 60)
    formatted_time = f"{hours}h {minutes}m {seconds}s"

    response = (
        f"📊 **Statistik {message.from_user.first_name}**:\n\n"
        f"🎮 Total Permainan: {stats['games_played']}\n"
        f"🏆 Kemenangan: {stats['games_won']}\n"
        f"😞 Kekalahan: {stats['games_lost']}\n"
        f"🤝 Seri: {stats['games_draw']}\n"
        f"⏳ Total Waktu Bermain: {formatted_time}\n"
    )

    bot.send_message(message.chat.id, response, reply_markup=CONTACT_KEYS)

# Inline query handler
@app.on_inline_query()
def inline_query_handler(_, query: InlineQuery):
    query.answer(
        results=[InlineQueryResultArticle(
            title="Tic-Tac-Toe",
            input_message_content=InputTextMessageContent(
                f"**{query.from_user.first_name}** menantang untuk bermain!"
            ),
            description="Pencet di sini untuk menantang temanmu!",
            thumb_url="https://upload.wikimedia.org/wikipedia/commons/3/32/Tic_tac_toe.svg",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("⚔️ Accept", callback_data=json.dumps({"type": "P", "id": query.from_user.id}))]]
            )
        )],
        cache_time=1
    )

# Callback query handler
@app.on_callback_query()
def callback_query_handler(bot: Client, query: CallbackQuery):
    try:
        data = json.loads(query.data)
        # Handle specific callback data types (P, K, R, C)
        # Implementation omitted for brevity; similar to the original logic
    except Exception as e:
        bot.answer_callback_query(query.id, f"Terjadi kesalahan: {e}", show_alert=True)

# Run the bot
if __name__ == "__main__":
    print("Bot berjalan sekarang!")
    app.run()