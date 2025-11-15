import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.user.router import router as auth_router
from app.api.router import router as api_router
from app.api.dao import BlogDAO
from app.api.views import router as blog_router

app = FastAPI()

# настраиваем статические файлы
app.mount('/static', StaticFiles(directory='app/static'), name='static') # подприложение StaticFiles обслуживает все запросы пути /static

app.include_router(auth_router)
app.include_router(api_router)
app.include_router(blog_router)

async def main():
    await BlogDAO.delete_by_id(1)


if __name__ == "__main__":
    asyncio.run(main())