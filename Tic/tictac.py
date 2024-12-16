import json
from Tic.emoji import *
from pyrogram.types import InlineKeyboardButton

class ErGame:
    def __init__(self, game_id: str, player1: dict, player2: dict = None) -> None:
        self.game_id = game_id
        self.player1 = player1
        self.player2 = player2
        self.winner = None
        self.winner_keys = []
        self.whose_turn = True  # True: Player1, False: Player2
        self.board = [[0] * 3 for _ in range(3)]
        self.board_keys = [[InlineKeyboardButton(".", callback_data=f"K:{i}:{j}") for j in range(3)] for i in range(3)]

    def is_draw(self) -> bool:
        if any(0 in row for row in self.board):
            return False

        # Update all buttons to final state
        self.update_buttons(final=True)
        return True

    def fill_board(self, player_id: int, coord: tuple) -> bool:
        if self.board[coord[0]][coord[1]] != 0:
            return False

        symbol = 1 if player_id == self.player1["id"] else 2
        emoji = "X" if symbol == 1 else "O"
        self.board[coord[0]][coord[1]] = symbol
        self.board_keys[coord[0]][coord[1]] = InlineKeyboardButton(
            emoji, callback_data=f"K:{coord[0]}:{coord[1]}:F"
        )
        return True

    def check_winner(self) -> bool:
        # Define all possible winning conditions
        lines = [
            # Rows
            [(0, 0), (0, 1), (0, 2)],
            [(1, 0), (1, 1), (1, 2)],
            [(2, 0), (2, 1), (2, 2)],
            # Columns
            [(0, 0), (1, 0), (2, 0)],
            [(0, 1), (1, 1), (2, 1)],
            [(0, 2), (1, 2), (2, 2)],
            # Diagonals
            [(0, 0), (1, 1), (2, 2)],
            [(0, 2), (1, 1), (2, 0)],
        ]

        for line in lines:
            values = [self.board[x][y] for x, y in line]
            if values[0] != 0 and values.count(values[0]) == 3:
                self.winner = self.player1 if values[0] == 1 else self.player2
                self.winner_keys = line
                self.update_buttons(final=True)
                return True

        return False

    def update_buttons(self, final: bool = False):
        for i in range(3):
            for j in range(3):
                symbol = self.board[i][j]
                if symbol == 0:
                    emoji = "." if not final else " "
                elif symbol == 1:
                    emoji = "X" if final and (i, j) in self.winner_keys else "X"
                else:
                    emoji = "O" if final and (i, j) in self.winner_keys else "O"
                self.board_keys[i][j] = InlineKeyboardButton(
                    emoji, callback_data=f"K:{i}:{j}:{'F' if final else 'P'}"
                )

        if final:
            self.board_keys.append(
                [InlineKeyboardButton("Play Again!", callback_data="R")]
            )