from beanie import init_beanie
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from zodiac.api.routes import auth_router, members_router, teams_router
from zodiac.config import MONGO_URL
from zodiac.entities.db.employee import Employee
from zodiac.entities.db.team import Team
from zodiac.entities.db.user import User


app = FastAPI(title="Astro API", version="0.0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://sosiska.work",
        "https://bubilda.sosiska.work",
        "https://localhost:3000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, prefix="/api/v1")
app.include_router(teams_router, prefix="/api/v1")
app.include_router(members_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    client = AsyncIOMotorClient(MONGO_URL)
    await init_beanie(
        database=client.zodiac,
        document_models=[User, Employee, Team],
    )
