from blacksheep import Application
from blacksheep.server.openapi.v3 import OpenAPIHandler
from openapidocs.v3 import Info
# from beanie import init_beanie
# import motor.motor_asyncio

from zodiac.api.routes import TeamsController
from zodiac.api.auth import jwt_authentication_handler
from zodiac.config import MONGO_URL
from zodiac.entities.db.employee import Employee
from zodiac.entities.db.team import Team
from zodiac.entities.db.user import User

app = Application()
app.register_controllers([TeamsController])
app.use_authentication().add(jwt_authentication_handler)

docs = OpenAPIHandler(info=Info(title="Astro API", version="0.0.1"))
docs.bind_app(app)

@app.on_start
async def on_start():
    ...
    # client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    # await init_beanie(
    #     database=client.get_default_database(),
    #     document_models=[User, Employee, Team],
    # )
