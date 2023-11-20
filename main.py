import asyncio
from app.utils.config import conf
from app.utils import logs
from app.modules.sites import Sites
from app.modules.bot import run_bot

async def main():
    print("Main program logic...")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    tasks = [run_bot(), main()]
    loop.run_until_complete(asyncio.gather(*tasks))