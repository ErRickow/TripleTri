from Tic.tictac import ErGame
import json

games = []


def get_game(game_id: str, player: dict = None) -> ErGame:
    for game in games:
        if game.game_id == game_id:
            return game
    games.append(ErGame(game_id, player))
    return games[-1]


def remove_game(game_id: str) -> bool:
    for index in range(len(games)):
        if games[index].game_id == game_id:
            games.pop(index)
            return True
    return False


def reset_game(game: ErGame) -> ErGame:
    temp_game_id = game.game_id
    temp_p1 = game.player2
    temp_p2 = game.player1

    if remove_game(game.game_id):
        games.append(ErGame(temp_game_id, temp_p1, temp_p2))
        return games[-1]
 
# Fungsi untuk memuat statistik pengguna
def load_stats():
    try:
        with open("user_stats.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Fungsi untuk menyimpan statistik pengguna
def save_stats(stats):
    with open("user_stats.json", "w") as file:
        json.dump(stats, file)

# Fungsi untuk memperbarui statistik
def update_stats(user_id, result):
    stats = load_stats()

    if user_id not in stats:
        stats[user_id] = {"games_played": 0, "games_won": 0, "games_draw": 0}

    stats[user_id]["games_played"] += 1
    if result == "win":
        stats[user_id]["games_won"] += 1
    elif result == "draw":
        stats[user_id]["games_draw"] += 1

    save_stats(stats)

        