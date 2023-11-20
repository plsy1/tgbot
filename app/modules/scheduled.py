import asyncio, schedule
from app.utils.config import conf
from app.modules.sites import sites
from app.utils.logs import log_background_info
from app.utils.logs import log_error_info


async def site_auto_sign(bot):
    
    schedule.every().day.at(conf.auto_signin_interval).do(lambda: asyncio.create_task(run_auto_sign_task(bot)))

    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

async def run_auto_sign_task(bot):
    # 创建一个任务并运行协程
    asyncio.ensure_future(run_auto_sign(bot))
    
async def run_auto_sign(bot):
    await asyncio.get_event_loop().run_in_executor(None, log_background_info, '开始执行自动签到')
    future = asyncio.get_event_loop().run_in_executor(None, sites.sigin_in)
    res = await future
    try:
        await bot.send_message(conf.chat_id, res, parse_mode='Markdown')
    except Exception as e:
        log_error_info("Error in Auto Signin message send: ", e)


async def auto_cookies_update():
    print('设置cookies定时更新')
    schedule.every(int(conf.cookiecloud_interval)).seconds.do(lambda: asyncio.create_task(run_auto_cookies_update_task()))

    while True:
        schedule.run_pending()
        await asyncio.sleep(1)
        
async def run_auto_cookies_update_task():
    asyncio.ensure_future(run_auto_cookies_update())
    
async def run_auto_cookies_update():
    await asyncio.get_event_loop().run_in_executor(None, log_background_info, '开始执行Cookies自动更新')
    asyncio.get_event_loop().run_in_executor(None, sites.update_cookies)
    
    
    