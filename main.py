import asyncio
from app.utils.config import conf
from app.utils import logs
from app.modules.database import initialize_database
from app.modules.sites import Sites
from app.modules.bot import run_bot, bot
from app.modules.scheduled import auto_cookies_update, auto_clear_sign_status, auto_update_site_info,auto_gen_audio_rss, auto_check_container_status

from app.plugins.audiobooksfeed.metadata import *
from app.plugins.audiobooksfeed.rss import *
from app.plugins.audiobooksfeed.server import *


async def audiobooks():
    file_server = FileServer(conf.root_folder)
    app_runner = web.AppRunner(file_server.app)
    await app_runner.setup()
    site = web.TCPSite(app_runner, host=get_preferred_ip_address(), port=int(conf.server_port))

    try:
        await site.start()
        while True:
            await asyncio.sleep(1)

    except asyncio.CancelledError:
        pass

    finally:
        await site.stop()
        await app_runner.cleanup()

async def main():
    asyncio.create_task(auto_cookies_update())
    asyncio.create_task(auto_clear_sign_status())
    asyncio.create_task(auto_update_site_info())
    asyncio.create_task(auto_gen_audio_rss(bot))
    asyncio.create_task(auto_check_container_status(bot))
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    tasks = [run_bot(), main()]
    loop.run_until_complete(asyncio.gather(*tasks))
    #generate_rss_file()
  