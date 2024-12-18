import os
from urllib.parse import quote
from Tic.data import *
from config import LOGS_GROUP_ID, MUST_JOIN, ownr, botid
from Tic.emoji import *
from Tic.util import dB
from Tic.erornya import bajingan
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, \
    InlineKeyboardMarkup, CallbackQuery, Message, InlineKeyboardButton

load_dotenv()

app = Client("er",
             api_id=os.environ.get("API_ID"),
             api_hash=os.environ.get("API_HASH"),
             bot_token=os.environ.get("BOT_TOKEN")
             )

IS_BROADCASTING = False

def mention(name: str, id: int) -> str:
    try:
        return "[{}](tg://user?id={})".format(name, id)
    except Exception as e:
        return f"Error: {e}"

CONTACT_KEYS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            cat + " Support",
            url="t.me/er_support_group"
        ),
        InlineKeyboardButton(
            id + " Owner",
            url="t.me/chakszzz"
        )
    ],
    [
        InlineKeyboardButton(
            mail + " Email",
            json.dumps({
                "type": "C",
                "action": "email"
            })
        )
    ]
])

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
                app.send_message(
                    LOGS_GROUP_ID,
                    f"Bang {msg.from_user.mention} gabung dahulu ke {channel}."
                )
                if channel.isalpha():
                    link = "https://t.me/" + channel
                else:
                    chat_info = app.get_chat(channel)
                    link = chat_info.invite_link
                try:
                    app.send_message(
                        msg.chat.id,
                        f"Untuk menggunakan bot ini, kamu harus bergabung dulu ke channel kami [di sini]({link}). Setelah bergabung, silakan ketik /start kembali.",
                        effect_id=5107584321108051014,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton("🔗 GABUNG SEKARANG", url=link),
                                ]
                            ]
                        )
                    )
                    msg.stop_propagation()
                except ChatWriteForbidden:
                    pass
    except ChatAdminRequired:
        app.send_message(LOGS_GROUP_ID, f"Bot perlu diangkat sebagai admin di grup/channel yang diminta: {MUST_JOIN} !")

@app.on_message(filters.command("start") & filters.private)
@bajingan
def start_handler(bot: Client, message: Message):
    brod = dB.get_list_from_var(app.me.id, "BROADCAST")
    if message.from_user.id not in brod:
        dB.add_to_var(bot.me.id, "BROADCAST", message.from_user.id)
    bot.send_message(
        message.chat.id,
        f"Hi **{message.from_user.first_name}**\n\nUntuk memulai, start terlebih dahulu, "
        f"dengan {bot.me.mention} di group kamu atau klik Tombol **Bermain** "
        "dan pilih group mana pun.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "🎮",
                switch_inline_query=game
            )]
        ])
    )

@app.on_message(filters.command("contact") & filters.private)
@bajingan
def contact_handler(bot: Client, message: Message):
    brod = dB.get_list_from_var(app.me.id, "BROADCAST")
    if message.from_user.id not in brod:
        dB.add_to_var(bot.me.id, "BROADCAST", message.from_user.id)
    bot.send_message(
        message.chat.id,
        "Bebas saran ke owner.",
        reply_to_message_id=message.id,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Hubungi owner", url="https://t.me/chakszzz")],
            [InlineKeyboardButton("Admin Side", url="https://t.me/Dvllll023")]
        ])
    )

@app.on_message(filters.command("stats") & filters.group)
@bajingan
def stats_handler(bot: Client, message: Message):
    user_id = message.from_user.id
    stats = dB.get_user_stats(user_id)
    chatid = message.chat.id

    # Pengecekan apakah chat ID sudah masuk ke database
    if not dB.is_served_chat(chatid):  # Jika chat ID belum ada
        dB.add_served_chat(chatid)  # Tambahkan chat ID ke database

    # Format waktu bermain
    hours, remainder = divmod(stats["total_play_time"], 3600)
    minutes, seconds = divmod(remainder, 60)
    formatted_time = f"{hours}h {minutes}m {seconds}s"

    # Pesan respons statistik
    response = (
        f"📊 **Statistik {message.from_user.first_name}**:\n\n"
        f"🎮 Total Permainan: {stats['games_played']}\n"
        f"🏆 Kemenangan: {stats['games_won']}\n"
        f"😞 Kekalahan: {stats['games_lost']}\n"
        f"🤝 Seri: {stats['games_draw']}\n"
        f"⏳ Total Waktu Bermain: {formatted_time}\n"
    )

    bot.send_message(message.chat.id, response, reply_markup=CONTACT_KEYS)

@app.on_inline_query()
def inline_query_handler(_, query: InlineQuery):
    try:
        
        namanya = query.from_user.first_name
        if not namanya:
            namanya = query.from_user.mention
    except Exception as e:
        namanya = query.from_user.mention
        
    
    query.answer(
        results=[InlineQueryResultArticle(
            title="Tic-Tac-Toe",
            input_message_content=InputTextMessageContent(
                f"**{namanya} Menantang untuk bermain!**"
            ),
            description="Pencet Disini Untuk Menantang Temanmu!",
            thumb_url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Tic_tac_toe.svg/1200px-Tic_tac_toe"
                      ".svg.png",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(
                    swords + " Terima",
                    json.dumps(
                        {"type": "P",
                         "id": query.from_user.id,
                         "name": query.from_user.username
                         }
                    )
                )]]
            )
        )],
        cache_time=1
    )


@app.on_callback_query()
def callback_query_handler(bot: Client, query: CallbackQuery):
    data = json.loads(query.data)
    game = get_game(query.inline_message_id, data)
    if data["type"] == "P":  # Player
        if game.player1["id"] == query.from_user.id:
            bot.answer_callback_query(
                query.id,
                "Tunggu Sebentar!",
                show_alert=True
            )
        elif game.player1["id"] != query.from_user.id:
            game.player2 = {"type": "P",
                            "id": query.from_user.id,
                            "name": query.from_user.first_name
                            }

            message_text = "{}({})  {}  {}({})\n\n{} **{} ({})**".format(
                mention(game.player1["name"], game.player1["id"]),
                X,
                vs,
                mention(game.player2["name"], game.player2["id"]),
                O,
                game,
                mention(game.player1["name"], game.player1["id"]),
                X
            )

            bot.edit_inline_text(
                query.inline_message_id,
                message_text,
                reply_markup=InlineKeyboardMarkup(game.board_keys)
            )
    elif data["type"] == "K":  # Keyboard
        if data["end"]:
            bot.answer_callback_query(
                query.id,
                "Game Berakhir!",
                show_alert=True
            )

            return

        if (game.whose_turn and query.from_user.id != game.player1["id"]) \
                or (not game.whose_turn and query.from_user.id != game.player2["id"]):
            bot.answer_callback_query(
                query.id,
                "Bukan Giliranmu!"
            )

            return

        if game.fill_board(query.from_user.id, data["coord"]):
            game.whose_turn = not game.whose_turn

            if game.check_winner():
                message_text = "{}({})  {}  {}({})\n\n{} **{} won!**".format(
                    mention(game.player1["name"], game.player1["id"]),
                    X,
                    vs,
                    mention(game.player2["name"], game.player2["id"]),
                    O,
                    trophy,
                    mention(game.winner["name"], game.winner["id"])
                )
            elif game.is_draw():
                message_text = "{}({})  {}  {}({})\n\n{} **Draw!**".format(
                    mention(game.player1["name"], game.player1["id"]),
                    X,
                    vs,
                    mention(game.player2["name"], game.player2["id"]),
                    O,
                    draw
                )
            else:
                message_text = "{}({})  {}  {}({})\n\n{} **{} ({})**".format(
                    mention(game.player1["name"], game.player1["id"]),
                    X,
                    vs,
                    mention(game.player2["name"], game.player2["id"]),
                    O,
                    game,
                    mention(game.player1["name"], game.player1["id"]) if game.whose_turn else
                    mention(game.player2["name"], game.player2["id"]),
                    X if game.whose_turn else O
                )

            bot.edit_inline_text(
                query.inline_message_id,
                message_text,
                reply_markup=InlineKeyboardMarkup(game.board_keys)
            )
        else:
            bot.answer_callback_query(
                query.id,
                "Ini bukan room kamu!"
            )
    elif data["type"] == "R":  # Reset
        game = reset_game(game)

        message_text = "{}({})  {}  {}({})\n\n{} **{} ({})**".format(
            mention(game.player1["name"], game.player1["id"]),
            X,
            vs,
            mention(game.player2["name"], game.player2["id"]),
            O,
            game,
            mention(game.player1["name"], game.player1["id"]),
            X
        )

        bot.edit_inline_text(
            query.inline_message_id,
            message_text,
            reply_markup=InlineKeyboardMarkup(game.board_keys)
        )
    elif data["type"] == "C":  # Contact
        if data["action"] == "email":
            bot.edit_message_text(
                query.from_user.id,
                query.message.message_id,
                "ryppain@gmail.com",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(
                        back + " Kembali",
                        json.dumps(
                            {"type": "C",
                             "action": "email-back"
                             }
                        )
                    )]]
                )
            )
        elif data["action"] == "email-back":
            bot.edit_message_text(
                query.from_user.id,
                query.message.message_id,
                "Feel free to share your thoughts bot with me.",
                reply_markup=CONTACT_KEYS
            )

@app.on_message(filters.command("bro"))
@bajingan
async def broadcast_message(client, message):
    global IS_BROADCASTING
    sudoers = dB.get_list_from_var(client.me.id, "sudoers", "userid")
    sudoers.append(ownr)
    if message.from_user.id not in sudoers:
        return message.reply("❌ Kamu bukan pengguna sudo.")
    elif message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
    else:
        if len(message.command) < 2:
            return await message.reply_text("❗ Perintah tidak lengkap. Berikan teks atau balas pesan untuk broadcast.")
        query = message.text.split(None, 1)[1]
        if "-pin" in query:
            query = query.replace("-pin", "")
        if "-nobot" in query:
            query = query.replace("-nobot", "")
        if "-pinloud" in query:
            query = query.replace("-pinloud", "")
        if "-user" in query:
            query = query.replace("-user", "")
        if query == "":
            return await message.reply_text("❗ Berikan tipe broadcast atau teks yang sesuai.")

    IS_BROADCASTING = True

    # Bot broadcast inside chats
    if "-nobot" not in message.text:
        sent = 0
        pin = 0
        chats = []
        schats = dB.get_served_chats()  # Mengambil semua served chats dari database
        chats = [int(chat["chat_id"]) for chat in schats]
        for i in chats:
            if i == LOGS_GROUP_ID:
                continue
            try:
                m = (
                    await client.forward_messages(i, y, x)
                    if message.reply_to_message
                    else await client.send_message(i, text=query)
                )
                if "-pin" in message.text:
                    try:
                        await m.pin(disable_notification=True)
                        pin += 1
                    except Exception:
                        continue
                elif "-pinloud" in message.text:
                    try:
                        await m.pin(disable_notification=False)
                        pin += 1
                    except Exception:
                        continue
                sent += 1
            except FloodWait as e:
                flood_time = int(e.value)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except Exception:
                continue
        try:
            await message.reply_text(
                f"✅ **Broadcast selesai!**\n\n"
                f"📨 Pesan berhasil dikirim ke **{sent} grup**.\n"
                f"📌 **{pin} pesan dipin** dalam grup."
            )
        except:
            pass

    # Bot broadcasting to users
    if "-user" in message.text:
        susr = 0
        susers = dB.get_list_from_var(client.me.id, "BROADCAST")  # Mengambil data broadcast users
        for user_id in susers:
            try:
                m = (
                    await client.forward_messages(user_id, y, x)
                    if message.reply_to_message
                    else await client.send_message(user_id, text=query)
                )
                susr += 1
            except FloodWait as e:
                flood_time = int(e.value)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except Exception:
                pass
        try:
            await message.reply_text(
                f"✅ **Broadcast selesai!**\n\n"
                f"📨 Pesan berhasil dikirim ke **{susr} pengguna.**"
            )
        except:
            pass
    IS_BROADCASTING = False
    
@app.on_message(filters.command("addsudo") & filters.user(ownr))
def add_sudo(client, message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user = message.reply_to_message.from_user
    else:
        user_id = message.command[1] if len(message.command) > 1 else None
        if not user_id or not user_id.isdigit():
            return message.reply("❌ Harap reply ke pengguna atau berikan ID pengguna yang valid.")

        try:
            user = client.get_users(int(user_id))
        except Exception as error:
            return message.reply(f"❌ Terjadi kesalahan saat mencari pengguna: {error}")

    sudoers = dB.get_list_from_var(client.me.id, "sudoers", "userid")
    sudoers.append(ownr)  # Pastikan pemilik bot juga ada dalam daftar sudoers
    usro = f"[{user.first_name} {user.last_name or ''}](tg://user?id={user.id})"

    if user.id in sudoers:
        return message.reply(f"✅ {usro} sudah ada dalam daftar sudo.")

    try:
        dB.add_to_var(client.me.id, "sudoers", user.id, "userid")
        return message.reply(f"✅ Berhasil menambahkan {usro} ke daftar sudo.")
    except Exception as error:
        return message.reply(f"❌ Terjadi kesalahan: {error}")


@app.on_message(filters.command("delsudo") & filters.user(ownr))
def del_sudo(client, message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user = message.reply_to_message.from_user
    else:
        user_id = message.command[1] if len(message.command) > 1 else None
        if not user_id or not user_id.isdigit():
            return message.reply("❌ Harap reply ke pengguna atau berikan ID pengguna yang valid.")

        try:
            user = client.get_users(int(user_id))
        except Exception as error:
            return message.reply(f"❌ Terjadi kesalahan saat mencari pengguna: {error}")

    sudoers = dB.get_list_from_var(client.me.id, "sudoers", "userid")
    sudoers.append(ownr)  # Pastikan pemilik bot juga ada dalam daftar sudoers
    usro = f"[{user.first_name} {user.last_name or ''}](tg://user?id={user.id})"

    if user.id not in sudoers:
        return message.reply(f"✅ {usro} tidak ditemukan dalam daftar sudo.")

    try:
        dB.remove_from_var(client.me.id, "sudoers", user.id, "userid")
        return message.reply(f"✅ Berhasil menghapus {usro} dari daftar sudo.")
    except Exception as error:
        return message.reply(f"❌ Terjadi kesalahan: {error}")


@app.on_message(filters.command("sudolist") & filters.user(ownr))
def sudo_list(client, message):
    msg = "📋 **Daftar Sudo:**\n\n"
    sudoers = dB.get_list_from_var(client.me.id, "sudoers", "userid")
    sudoers.append(ownr)  # Pastikan pemilik bot juga ada dalam daftar sudoers

    if not sudoers:
        return message.reply("❌ Daftar sudo kosong.")

    for user_id in sudoers:
        try:
            user = client.get_users(int(user_id))
            user_name = user.mention if user.mention else user.first_name
            msg += f"• {user_name}\n"
        except Exception:
            msg += f"• ID: {user_id}\n"

    return message.reply(msg)

if __name__ == "__main__":
    print("im on now")
    app.run()
