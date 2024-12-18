import os

from Tic.data import *
from Tic.emoji import *
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, \
    InlineKeyboardMarkup, CallbackQuery, Message, InlineKeyboardButton

load_dotenv()

app = Client("er",
             api_id=os.environ.get("API_ID"),
             api_hash=os.environ.get("API_HASH"),
             bot_token=os.environ.get("BOT_TOKEN")
             )


def mention(name: str, id: int) -> str:
    return "[{}](tg://user?id={})".format(name, id)

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


@app.on_message(filters.command("start"))
def start_handler(bot: Client, message: Message):
    bot.send_message(
        message.chat.id,
        f"Hi **{message.from_user.first_name}**\n\nUntuk memulai, start terlebih dahulu, "
        "dengan @TripleTBot di group kamu atau klik Tombol **Bermain** "
        "dan pilih group mana pun.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "🎮 Bermain",
                switch_inline_query="Bermain"
            )]
        ])
    )

@app.on_message(filters.command("contact"))
def contact_handler(bot: Client, message: Message):
    bot.send_message(
        message.chat.id,
        "Feel free to share your thoughts on Telegram with me.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Hubungi Admin", url="https://t.me/your_username")]
        ])
    )

@app.on_message(filters.command("stats"))
def stats_handler(bot: Client, message: Message):
    user_id = message.from_user.id
    stats = dB.get_user_stats(user_id)

    hours, remainder = divmod(stats["total_play_time"], 3600)
    minutes, seconds = divmod(remainder, 60)
    formatted_time = f"{hours}h {minutes}m {seconds}s"

    response = (
        f"📊 **Statistik Anda**:\n\n"
        f"🎮 Total Permainan: {stats['games_played']}\n"
        f"🏆 Kemenangan: {stats['games_won']}\n"
        f"😞 Kekalahan: {stats['games_lost']}\n"
        f"🤝 Seri: {stats['games_draw']}\n"
        f"⏳ Total Waktu Bermain: {formatted_time}\n"
    )

    bot.send_message(message.chat.id, response, reply_markup=CONTACT_KEYS)

@app.on_inline_query()
def inline_query_handler(_, query: InlineQuery):
    query.answer(
        results=[InlineQueryResultArticle(
            title="Tic-Tac-Toe",
            input_message_content=InputTextMessageContent(
                f"**{query.from_user.first_name}** menantang untuk bermain!"
            ),
            description="Pencet Disini Untuk Menantang Temanmu!",
            thumb_url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Tic_tac_toe.svg/1200px-Tic_tac_toe"
                      ".svg.png",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(
                    swords + " Accept",
                    json.dumps(
                        {"type": "P",
                         "id": query.from_user.id,
                         "name": query.from_user.first_name
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

    

app.run()