import json

# Fungsi untuk memuat statistik pengguna
def load_stats():
    try:
        with open("user_stats.json", "r") as file:
            return json.load(file)  # Memuat data dari file JSON
    except FileNotFoundError:
        return {}  # Jika file tidak ditemukan, kembali dengan dictionary kosong

# Fungsi untuk menyimpan statistik pengguna
def save_stats(stats):
    try:
        with open("user_stats.json", "w") as file:
            json.dump(stats, file, indent=4)  # Menyimpan data dictionary ke dalam file JSON
    except Exception as e:
        print(f"Error saving stats: {e}")

# Fungsi untuk memperbarui statistik
def update_stats(user_id, result):
    stats = load_stats()  # Memuat data yang sudah ada

    # Inisialisasi statistik jika user belum ada dengan nilai None
    if user_id not in stats:
        stats[user_id] = {
            "games_played": None,
            "games_won": None,
            "games_lost": None,
            "games_draw": None
        }

    # Cek apakah statistik None, jika ya, inisialisasi dengan 0
    if stats[user_id]["games_played"] is None:
        stats[user_id]["games_played"] = 0
    if stats[user_id]["games_won"] is None:
        stats[user_id]["games_won"] = 0
    if stats[user_id]["games_lost"] is None:
        stats[user_id]["games_lost"] = 0
    if stats[user_id]["games_draw"] is None:
        stats[user_id]["games_draw"] = 0

    # Update total permainan
    stats[user_id]["games_played"] += 1

    if result == "win":
        stats[user_id]["games_won"] += 1  # Hanya tambah satu jika menang
    elif result == "lose":
        stats[user_id]["games_lost"] += 1  # Hanya tambah satu jika kalah
    elif result == "draw":
        stats[user_id]["games_draw"] += 1  # Hanya tambah satu jika seri

    # **Simpan perubahan pada statistik user**
    save_stats(stats)  # Simpan statistik setelah update
