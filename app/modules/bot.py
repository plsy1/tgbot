from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup
from functools import partial
from app.plugins.audiobooksfeed.rss import gen_new_audio_rss




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
from app.utils.sign_in_utils import clear_sign_status

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
            telebot.types.BotCommand("/signin", "强制重新签到"),
            telebot.types.BotCommand("/autosign", "开启自动签到"),
            telebot.types.BotCommand("/pauseall","暂停下载器任务"),
            telebot.types.BotCommand("/resumeall","恢复下载器任务"),
            telebot.types.BotCommand("/statistics","所有站点数据"),      
            telebot.types.BotCommand("/statistic","单个站点数据"),
            telebot.types.BotCommand("/new_audiobooks","生成新的本地有声书RSS地址")                     
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

@bot.message_handler(commands=['statistic'])
async def start(message: Message):
    keyboard = InlineKeyboardMarkup()
    
    # 添加按钮到键盘
    button1 = InlineKeyboardButton("杜比", callback_data="www.hddolby.com")
    button2 = InlineKeyboardButton("家园", callback_data="hdhome.org")
    button3 = InlineKeyboardButton("红叶", callback_data="leaves.red")
    
    button4 = InlineKeyboardButton("学校", callback_data="pt.btschool.club")
    button5 = InlineKeyboardButton("HDVideo", callback_data="hdvideo.one")
    button6 = InlineKeyboardButton("聆音", callback_data="pt.soulvoice.club")
    
    button7 = InlineKeyboardButton("Ubits", callback_data="ubits.club")
    button8 = InlineKeyboardButton("红豆饭", callback_data="hdfans.org")
    button9 = InlineKeyboardButton("海胆", callback_data="www.haidan.video")
    
    button10 = InlineKeyboardButton("srvfi", callback_data="www.srvfi.top")
    button11 = InlineKeyboardButton("馒头", callback_data="xp.m-team.io")
    button12 = InlineKeyboardButton("织梦", callback_data="zmpt.cc")
    
    button13 = InlineKeyboardButton("U2", callback_data="u2.dmhy.org")
    button14 = InlineKeyboardButton("Kamept", callback_data="kamept.com")
    button15 = InlineKeyboardButton("麒麟", callback_data="www.hdkyl.in")
    
    button16 = InlineKeyboardButton("oldtoons", callback_data="oldtoons.world")
    button17 = InlineKeyboardButton("rousi", callback_data="rousi.zip")
    button18 = InlineKeyboardButton("铂金学院", callback_data="ptchina.org")
    
    button19 = InlineKeyboardButton("TTG", callback_data="totheglory.im")
    
    
    keyboard.add(button1, button2, button3)
    keyboard.add(button4, button5, button6)
    keyboard.add(button7, button8, button9)
    keyboard.add(button10, button11, button12)
    keyboard.add(button13, button14, button15)
    keyboard.add(button16, button17, button18)
    keyboard.add(button19)

    # 发送包含按钮的键盘给用户
    await bot.send_message(message.chat.id, "点击按钮查看对应站点数据统计信息嗷", reply_markup=keyboard)
    

@bot.callback_query_handler(func=lambda call: True)
async def handle_button_click(call):
        res = await asyncio.get_event_loop().run_in_executor(None, sites.update_and_show_site_info, call.data)
        await bot.send_message(call.message.chat.id, res, parse_mode='Markdown')


        

@bot.message_handler(commands=['new_audiobooks'])
@check_chat_id
async def new_audiobooks(message):
    await bot_callback(bot, message,gen_new_audio_rss,handle_result)


@bot.message_handler(commands=['statistics'])
@check_chat_id
async def statistics(message):
    await bot_callback(bot, message,sites.statistics,handle_result)
    
@bot.message_handler(commands=['signin'])
@check_chat_id
async def signin(message):
    await asyncio.get_event_loop().run_in_executor(None, clear_sign_status)
    await bot_callback(bot, message,sites.sign_in,handle_result)
    
@bot.message_handler(commands=['autosign'])
@check_chat_id
async def autosign(message):
    if(sites.auto_sign_is_open == True):
        await safe_reply(bot, message, "自动签到已经打开咧，你还想开第二次？", parse_mode='Markdown')
    else:
        asyncio.create_task(site_auto_sign(bot))
        await safe_reply(bot, message, "自动签到开启成功，开了就关不掉了嗷！", parse_mode='Markdown')
        sites.auto_sign_is_open = True
    
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
    
    
    
