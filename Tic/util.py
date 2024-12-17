import json

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
        json.dump(stats, file, indent=4)

# Fungsi untuk memperbarui statistik
def update_stats(user_id, result):
    stats = load_stats()

    # Inisialisasi statistik jika user belum ada
    if user_id not in stats:
        stats[user_id] = {
            "games_played": 0,
            "games_won": 0,
            "games_lost": 0,
            "games_draw": 0
        }

    # Update total permainan
    stats[user_id]["games_played"] += 1

    # Update berdasarkan hasil permainan
    if result == "win":
        stats[user_id]["games_won"] += 1
    elif result == "lose":
        stats[user_id]["games_lost"] += 1
    elif result == "draw":
        stats[user_id]["games_draw"] += 1

    save_stats(stats)