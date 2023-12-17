import asyncio, schedule
import random
from datetime import datetime
from app.utils.config import conf
from app.modules.sites import sites
from app.utils.logs import log_background_info
from app.utils.logs import log_error_info
from app.modules.database import clear_sign_status
from app.plugins.audiobooksfeed.rss import gen_new_audio_rss
from app.plugins.containerstatuscheck.main import container_status_check
from app.modules.database import get_sites



async def site_auto_sign(bot):
    async def run_auto_sign_task():
        await asyncio.ensure_future(run_auto_sign())

    async def run_auto_sign():
        await asyncio.get_event_loop().run_in_executor(None, log_background_info, '开始执行自动签到')
        future = asyncio.get_event_loop().run_in_executor(None, sites.sign_in)
        res = await future
        try:
            await bot.send_message(conf.chat_id, res, parse_mode='Markdown')
        except Exception as e:
            log_error_info("Error in Auto Signin message send: ", e)
    async def generate_random_time():
        random_hour = random.randint(8, 21)
        random_minute = random.randint(0, 59)

        random_time = f"{str(random_hour).zfill(2)}:{str(random_minute).zfill(2)}"

        return random_time
    
    
    random_time_one = await generate_random_time()
    random_time_two = await generate_random_time()
    while random_time_two == random_time_one:
        random_time_two = await generate_random_time()
        
    log_background_info(f'开启自动签到，自动执行时间为：{random_time_one}，{random_time_two}')
    job_one = schedule.every().day.at(random_time_one).do(lambda: asyncio.create_task(run_auto_sign_task()))
    job_two = schedule.every().day.at(random_time_two).do(lambda: asyncio.create_task(run_auto_sign_task()))
    
    last_update_date = datetime.now().date()
    log_background_info(f'自动签到执行时间生成于：{last_update_date}')
    
    while True:
        if last_update_date < datetime.now().date():  
    
            random_time_one = await generate_random_time()
            random_time_two = await generate_random_time()
            while random_time_two == random_time_one:
                random_time_two = await generate_random_time()
            log_background_info(f'更新自动签到执行时间: {random_time_one}，{random_time_two}')
            
            schedule.cancel_job(job_one)
            schedule.cancel_job(job_two)
            
            job_one = schedule.every().day.at(random_time_one).do(lambda: asyncio.create_task(run_auto_sign_task()))
            job_two = schedule.every().day.at(random_time_two).do(lambda: asyncio.create_task(run_auto_sign_task()))
            
            last_update_date = datetime.now().date()
            log_background_info(f'自动签到执行时间更新于: {last_update_date}')   
            
        schedule.run_pending()
        await asyncio.sleep(1)

async def auto_cookies_update():
    log_background_info('设置定时任务：站点Cookies自动更新')
    
    async def run_auto_cookies_update_task():
        await asyncio.get_event_loop().run_in_executor(None, log_background_info, '开始执行：Cookies自动更新')
        await asyncio.get_event_loop().run_in_executor(None, sites.update_cookies)

    schedule.every(int(conf.cookiecloud_interval)).seconds.do(
        lambda: asyncio.create_task(run_auto_cookies_update_task())
    )

    while True:
        schedule.run_pending()
        await asyncio.sleep(1)
    
    
async def auto_clear_sign_status():
    log_background_info('设置定时任务：每日还原所有站点签到状态为False')
    
    async def run_clear_sign_status_task():
        await asyncio.get_event_loop().run_in_executor(None, log_background_info, '开始执行：还原所有站点签到状态为False')
        await asyncio.get_event_loop().run_in_executor(None, clear_sign_status)

    schedule.every().day.at(conf.auto_clear_sign_status_time).do(
        lambda: asyncio.create_task(run_clear_sign_status_task())
    )

    while True:
        schedule.run_pending()
        await asyncio.sleep(1)
        
async def auto_update_site_info():
    log_background_info('设置定时任务：每日更新站点统计数据')
    
    async def run_update_site_info():
        await asyncio.get_event_loop().run_in_executor(None, log_background_info, '开始执行：每日更新站点统计数据')
        await asyncio.get_event_loop().run_in_executor(None, sites.update_site_info)

    schedule.every().day.at(conf.auto_clear_sign_status_time).do(
        lambda: asyncio.create_task(run_update_site_info())
    )

    while True:
        schedule.run_pending()
        await asyncio.sleep(1)
        
        
async def auto_gen_audio_rss(bot):
    log_background_info('设置定时任务：自动生成新入库有声书RSS地址')
    
    async def run_gen_audio_rss():
        await asyncio.get_event_loop().run_in_executor(None, log_background_info, '开始执行：自动生成新入库有声书RSS地址')
        rss_message = await asyncio.get_event_loop().run_in_executor(None, gen_new_audio_rss)
        if rss_message != '未检测到有声书入库。':
            await bot.send_message(conf.chat_id, rss_message)
    
    schedule.every(int(conf.audio_rss_gen_interval)).seconds.do(
        lambda: asyncio.create_task(run_gen_audio_rss())
    )

    while True:
        schedule.run_pending()
        await asyncio.sleep(1)
        
        
async def auto_check_container_status(bot):
    log_background_info('设置定时任务：自动检查容器运行状态')
    
    async def run_gen_audio_rss():
        await asyncio.get_event_loop().run_in_executor(None, log_background_info, '开始执行：自动检查容器运行状态')
        message = await asyncio.get_event_loop().run_in_executor(None, container_status_check)
        if message:
            await bot.send_message(conf.chat_id, message)
    
    schedule.every(int(conf.container_status_check_interval)).seconds.do(
        lambda: asyncio.create_task(run_gen_audio_rss())
    )

    while True:
        schedule.run_pending()
        await asyncio.sleep(1)