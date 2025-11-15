import asyncio
from fastapi import FastAPI
from app.user.router import router as auth_router
from app.api.router import router as api_router
from app.api.dao import BlogDAO

app = FastAPI()

app.include_router(auth_router)
app.include_router(api_router)


async def main():
    await BlogDAO.delete_by_id(1)


if __name__ == "__main__":
    asyncio.run(main())