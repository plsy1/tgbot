from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.modules.sites import sites
from back.api import sitesInfo, rssSearch
app = FastAPI()

# 允许所有来源访问，允许所有方法（GET, POST 等），允许所有头部
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/siteinfo")
def send():
    # 在这里调用 pauseqb() 函数，并获取结果
    return sitesInfo()

@app.post("/api/search")
async def search(request: Request):

    data = await request.json()

    search_query = data.get('search_query', '')
    print(search_query)
    api_results = rssSearch(search_query)


    return api_results