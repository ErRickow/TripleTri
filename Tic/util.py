from db import dB  # Pastikan Anda mengimpor dB
import time
from config import ownr, botid
from pyrogram import filters

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
    
def sudo():
    global SUDOERS
    SUDOERS = set()
    OWNER = ownr  # Daftar pemilik bot (OWNER)
    
    # Memuat sudoers dari database SQLite
    sudoers = dB.get_list_from_var(bot_id=botid, vars_name="sudoers", query="userid")

    # Tambahkan pemilik ke dalam SUDOERS
    for user_id in OWNER:
        SUDOERS.add(user_id)
        if user_id not in sudoers:
            dB.add_to_var(bot_id=botid, vars_name="sudoers", value=user_id, query="userid")

    # Tambahkan sudoers lain dari database
    if sudoers:
        for user_id in sudoers:
            SUDOERS.add(user_id)

    LOGGER(__name__).info("Sudoers Loaded.")