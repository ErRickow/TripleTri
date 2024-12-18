import traceback
from functools import wraps
from main import LOGS_GROUP_ID, app

def capture_err_simple(func):
    """Decorator untuk menangkap error dan mengirim log ke LOG_GROUP_ID."""
    @wraps(func)
    async def wrapper(app, message, *args, **kwargs):
        try:
            return await func(client, message, *args, **kwargs)
        except Exception as err:
            # Tangkap error dan kirim ke grup log
            error_message = (
                f"🚨 **Yank Eror**\n"
                f"👤 User: {message.from_user.mention if message.from_user else 'Unknown'}\n"
                f"💬 Command: `{message.text or message.caption}`\n"
                f"⚠️ Error: `{str(err)}`"
            )
            await app.send_message(LOGS_GROUP_ID, error_message)
            raise err
    return wrapper