import os

from Tic.data import *
from pyrogram import Client, filters
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, \
    InlineKeyboardMarkup, CallbackQuery, Message


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
            emoji.cat + " Support",
            url="t.me/er_support_group"
        ),
        InlineKeyboardButton(
            emoji.id + " Owner",
            url="t.me/chakszzz"
        )
    ],
    [
        InlineKeyboardButton(
            emoji.mail + " Email",
            json.dumps({
                "type": "C",
                "action": "email"
            })
        )
    ]
])


@app.on_message(filters.private & filters.text)
def message_handler(bot: Client, message: Message):
    if message.text == "/start":
        bot.send_message(
            message.from_user.id,
            f"Hi **{message.from_user.first_name}**\n\nTo begin, start a message "
            "with @ErGame in any chat you want or click on the **Play** button "
            "and select a chat to play in.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    emoji.game + " Play",
                    switch_inline_query=emoji.game
                )]
            ])
        )
    elif message.text == "/contact":
        bot.send_message(
            message.from_user.id,
            "Feel free to share your thoughts on Er bot with me.",
            reply_markup=CONTACT_KEYS
        )


@app.on_inline_query()
def inline_query_handler(_, query: InlineQuery):
    query.answer(
        results=[InlineQueryResultArticle(
            title="Tic-Tac-Toe",
            input_message_content=InputTextMessageContent(
                f"**{query.from_user.first_name}** challenged you in Game!"
            ),
            description="Tap here to challenge your friends!",
            thumb_url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Tic_tac_toe.svg/1200px-Tic_tac_toe"
                      ".svg.png",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(
                    emoji.swords + " Accept",
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
                emoji.X,
                emoji.vs,
                mention(game.player2["name"], game.player2["id"]),
                emoji.O,
                emoji.game,
                mention(game.player1["name"], game.player1["id"]),
                emoji.X
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
                "Not your turn!"
            )

            return

        if game.fill_board(query.from_user.id, data["coord"]):
            game.whose_turn = not game.whose_turn

            if game.check_winner():
                message_text = "{}({})  {}  {}({})\n\n{} **{} won!**".format(
                    mention(game.player1["name"], game.player1["id"]),
                    emoji.X,
                    emoji.vs,
                    mention(game.player2["name"], game.player2["id"]),
                    emoji.O,
                    emoji.trophy,
                    mention(game.winner["name"], game.winner["id"])
                )
            elif game.is_draw():
                message_text = "{}({})  {}  {}({})\n\n{} **Draw!**".format(
                    mention(game.player1["name"], game.player1["id"]),
                    emoji.X,
                    emoji.vs,
                    mention(game.player2["name"], game.player2["id"]),
                    emoji.O,
                    emoji.draw
                )
            else:
                message_text = "{}({})  {}  {}({})\n\n{} **{} ({})**".format(
                    mention(game.player1["name"], game.player1["id"]),
                    emoji.X,
                    emoji.vs,
                    mention(game.player2["name"], game.player2["id"]),
                    emoji.O,
                    emoji.game,
                    mention(game.player1["name"], game.player1["id"]) if game.whose_turn else
                    mention(game.player2["name"], game.player2["id"]),
                    emoji.X if game.whose_turn else emoji.O
                )

            bot.edit_inline_text(
                query.inline_message_id,
                message_text,
                reply_markup=InlineKeyboardMarkup(game.board_keys)
            )
        else:
            bot.answer_callback_query(
                query.id,
                "This one is already taken!"
            )
    elif data["type"] == "R":  # Reset
        game = reset_game(game)

        message_text = "{}({})  {}  {}({})\n\n{} **{} ({})**".format(
            mention(game.player1["name"], game.player1["id"]),
            emoji.X,
            emoji.vs,
            mention(game.player2["name"], game.player2["id"]),
            emoji.O,
            emoji.game,
            mention(game.player1["name"], game.player1["id"]),
            emoji.X
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
                "reza.farjam78@gmail.com",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(
                        emoji.back + " Back",
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