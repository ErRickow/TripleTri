from db import dB  # Pastikan Anda mengimpor dB
import time
from config import ownr, botid

def update_stats(user_id, result, start_time):
    stats = dB.get_user_stats(user_id)  # Ambil data dari database

    # Hitung durasi permainan
    play_time = int(time.time() - start_time)
    stats["total_play_time"] += play_time

    # Update total permainan
    stats["games_played"] += 1

    # Update berdasarkan hasil permainan
    if result == "win":
        stats["games_won"] += 1
    elif result == "lose":
        stats["games_lost"] += 1
    elif result == "draw":
        stats["games_draw"] += 1

    dB.save_user_stats(user_id, stats) 
   