import asyncio
from app.utils.config import conf
from app.utils import logs
from app.modules.database import initialize_database
from app.modules.sites import Sites
from app.modules.bot import run_bot
from app.modules.scheduled import auto_cookies_update, auto_clear_sign_status

async def main():
    asyncio.create_task(auto_cookies_update())
    asyncio.create_task(auto_clear_sign_status())

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    tasks = [run_bot(), main()]
    loop.run_until_complete(asyncio.gather(*tasks))