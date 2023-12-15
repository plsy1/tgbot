from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
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

@app.post("/api/search/{search_query}")
async def search(request: Request, search_query: str):
    api_results = rssSearch(search_query)

    return api_results

@app.get("/", status_code=302, tags=["html"])
def index():
    return RedirectResponse("/docs")

@app.post("/items/")
async def create_item(request: Request, item: dict):
    return {"item": item}