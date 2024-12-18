import traceback
from functools import wraps
from config import LOGS_GROUP_ID

def bajingan(func):
    """Decorator untuk menangkap error dan mengirim log ke LOG_GROUP_ID."""
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        try:
            return func(client, message, *args, **kwargs)
        except Exception as err:
            # Tangkap error dan kirim ke grup log
            error_message = (
                f"🚨 **Yank Eror**\n"
                f"👤 User: {message.from_user.mention if message.from_user else 'Unknown'}\n"
                f"💬 Command: `{message.text or message.caption}`\n"
                f"⚠️ Error: `{str(err)}`"
            )
            await client.send_message(LOGS_GROUP_ID, error_message)
            raise err
    return wrapper