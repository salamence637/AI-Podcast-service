from fastapi import FastAPI
from app.api import routes
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="DX Chat API",
    version="v0.0.1-alpha.1",
    # openapi_url="/v1/openapi.json",
    docs_url="/docs",
)


# FIXME: No properly configured
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(routes.router)
app.mount("/audio", StaticFiles(directory="audio"), name="audio")

# if __name__ == "__main__":
#     import uvicorn
#     # 使用 --reload 实现保存后自动重载（开发环境专用）
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
