# handlers.py

import asyncio
from app.modules.sites import sites
from app.utils.logs import log_error_info

async def handle_result(bot, message, result):
    try:
        await bot.reply_to(message, result, parse_mode='Markdown')
    except Exception as e:
        log_error_info("Error in bot reply: ", e)
        


async def bot_callback(bot, message, exec_func, callback_func):
    future = asyncio.get_event_loop().run_in_executor(None, exec_func)
    future.add_done_callback(lambda f: asyncio.create_task(callback_func(bot, message, f.result())))
