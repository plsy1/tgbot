from telebot.async_telebot import AsyncTeleBot
import telebot, asyncio
from app.utils.config import conf
from app.modules.sites import sites
from app.utils.handlers import bot_callback, handle_result
from app.modules.scheduled import site_auto_sign
from app.modules.qbittorrent import qb
from app.modules.transmission import tr
from app.utils.logs import log_bot_received_message
from app.utils.logs import log_bot_sent_message
from app.utils.logs import log_error_info


bot = AsyncTeleBot(conf.telegram_token)

async def safe_reply(bot, message, text, parse_mode=None):
    try:
        await bot.reply_to(message, text, parse_mode=parse_mode)
    except Exception as e:
        log_error_info("Error in bot reply: ", e)




async def commands(bot):
    try:
        await bot.delete_my_commands()
        await bot.set_my_commands([
            telebot.types.BotCommand("/speed", "查看下载器速度"),
            telebot.types.BotCommand("/signin", "手动签到"),
            telebot.types.BotCommand("/autosign", "开启自动签到"),
            telebot.types.BotCommand("/pauseall","暂停下载器任务"),
            telebot.types.BotCommand("/resumeall","恢复下载器任务")                        
        ])
    except telebot.asyncio_helper.RequestTimeout as e:
        log_error_info("Error deleting commands: ", e)

async def run_bot():
    await commands(bot)
    await bot.polling(none_stop=True, timeout=30)

def check_chat_id(func):
    async def wrapper(message):
        if str(message.chat.id) == conf.chat_id:
            await func(message)
        else:
            await bot.send_message(message.chat.id, "没有权限")

    return wrapper

@bot.message_handler(commands=['signin'])
@check_chat_id
async def signin(message):
    await asyncio.get_event_loop().run_in_executor(None, sites.update_cookies)
    await bot_callback(bot, message,sites.sigin_in,handle_result)
    
@bot.message_handler(commands=['autosign'])
@check_chat_id
async def autosign(message):
    asyncio.create_task(site_auto_sign(bot))
    await safe_reply(bot, message, "自动签到开启成功", parse_mode='Markdown')
    
@bot.message_handler(commands=['speed'])
@check_chat_id
async def downloadspeed(message):
    
    
    await asyncio.get_event_loop().run_in_executor(None, log_bot_received_message,message)
    res = "*[qBittorrent]*" \
       + (await asyncio.get_event_loop().run_in_executor(None, qb.speed_of_qb)) \
       + "\n" + "*[Transmission]*" \
       + await asyncio.get_event_loop().run_in_executor(None, tr.speed_of_tr)
    
    await safe_reply(bot, message, res, parse_mode='Markdown')
    await asyncio.get_event_loop().run_in_executor(None, log_bot_sent_message,message,res.replace('\n', ''))

@bot.message_handler(commands=['pauseall'])
@check_chat_id
async def autosign(message):
    await asyncio.get_event_loop().run_in_executor(None, log_bot_received_message,message)
    
    future = asyncio.get_event_loop().run_in_executor(None,qb.pause_all_qb)
    res = await future
    
    res += '\n'
    
    future = asyncio.get_event_loop().run_in_executor(None,tr.pause_all_tr)
    res += await future
    
    await safe_reply(bot, message, res, parse_mode='Markdown')
    await asyncio.get_event_loop().run_in_executor(None, log_bot_sent_message,message,res.replace('\n', ''))
    
    
@bot.message_handler(commands=['resumeall'])
@check_chat_id
async def autosign(message):
    await asyncio.get_event_loop().run_in_executor(None, log_bot_received_message,message)
    
    future = asyncio.get_event_loop().run_in_executor(None,qb.resume_all_qb)
    res = await future
    
    res += '\n'
    
    future = asyncio.get_event_loop().run_in_executor(None,tr.resume_all_tr)
    res += await future
    
    await safe_reply(bot, message, res, parse_mode='Markdown')
    await asyncio.get_event_loop().run_in_executor(None, log_bot_sent_message,message,res.replace('\n', ''))
    