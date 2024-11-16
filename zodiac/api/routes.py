from datetime import datetime
from blacksheep import FromJSON, FromQuery, Request, Response, json
from blacksheep.server.controllers import Controller, delete, get, patch, post, put
from pydantic import BaseModel, EmailStr
from passlib.hash import bcrypt
from blacksheep.server.authorization import allow_anonymous, auth

from zodiac.api.auth import authenticate_user, create_access_token
from zodiac.entities.dto.astro import AstroData
from zodiac.entities.db.employee import Employee
from zodiac.entities.dto.team import TeamDto
from zodiac.entities.enums.roles import Role
from zodiac.entities.dto.location import Location
from zodiac.entities.db.team import Team
from zodiac.entities.db.user import User
from zodiac.entities.dto.member import MemberDto
from zodiac.services.astrology import AstroChart

class AuthCredentials(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class TeamCreate(BaseModel):
    name: str
    description: str

class EmployeeCreate(BaseModel):
    full_name: str
    birth_date: datetime
    birth_place: Location
    email: EmailStr
    phone: str
    position: str

class ApplicantCreate(EmployeeCreate):
    pass

class TeamsController(Controller):
    @post("/auth/register")
    @allow_anonymous()
    async def register(self, data: FromJSON[UserCreate]):
        user = User(
            email=data.value.email,
            password_hash=bcrypt.hash(data.value.password),
            full_name=data.value.full_name,
        )
        await user.insert()
        return json({"message": "User registered successfully"})

    @post("/auth/login")
    @allow_anonymous()
    async def login(self, credentials: FromJSON[AuthCredentials]):
        user = await authenticate_user(credentials.value.email, credentials.value.password)
        if not user:
            return Response(401, content=b"Invalid credentials")
        token = create_access_token(str(user.id))
        return json({"access_token": token})

    @post("/teams")
    @auth()
    async def create_team(self, data: FromJSON[TeamCreate], request: Request):
        team = Team(
            name=data.value.name,
            description=data.value.description,
        )
        await team.insert()
        return json({"message": "Team created successfully", "team_id": str(team.id)})


    @get("/teams")
    @auth()
    async def list_teams(self):
        teams = await Team.find_all().to_list()
        return json([{"id": str(team.id), "name": team.name, "description": team.description} for team in teams])

    @get("/teams/{team_id}/members")
    @auth()
    async def list_employees(self, team_id: str, user: User):
        team = await Team.get(team_id, fetch_links=True)
        if not team:
            return Response(404, content=b"Team not found")

        team_members: list[Employee] = team.employees
        astro_charts: dict[str, AstroChart] = {}

        for member in team_members:
            astro_chart = AstroChart(
                birth_time=member.birth_date,
                latitude=member.birth_place.latitude,
                longitude=member.birth_place.longitude
            )
            astro_charts[str(member.id)] = astro_chart

        employees = []
        applicants = []

        for member in team_members:
            member_id = str(member.id)
            other_charts = [chart for mid, chart in astro_charts.items() if mid != member_id]
            compatibility = astro_charts[member_id].calculate_group_compatibility(other_charts)

            data = MemberDto(
                id=member_id,
                full_name=member.full_name,
                birth_date=member.birth_date,
                birth_place=member.birth_place,
                email=member.email,
                phone=member.phone,
                position=member.position,
                astro=AstroData(
                    personal_traits=member.astro.personal_traits,
                    compatibility=compatibility,
                )
            )

            if member.role == Role.EMPLOYEE:
                employees.append(data)
            elif member.role == Role.PENDING:
                applicants.append(data)

        return json(TeamDto(
            id=str(team.id),
            name=team.name,
            description=team.description,
            employees=employees,
            applicants=applicants,
        ).model_dump())

    @post("/teams/{team_id}/employees")
    @auth()
    async def add_employee(self, team_id: str, data: FromJSON[EmployeeCreate], request: Request):
        team = await Team.get(team_id)
        if not team:
            return Response(404, content=b"Team not found")
        employee = Employee(
            full_name=data.value.full_name,
            birth_date=data.value.birth_date,
            birth_place=data.value.birth_place,
            email=data.value.email,
            phone=data.value.phone,
            position=data.value.position,
            personal_traits=AstroChart(
                birth_time=data.value.birth_date,
                latitude=data.value.birth_place.latitude,
                longitude=data.value.birth_place.longitude
            ),
            role=Role.EMPLOYEE,
            team=team,
        )
        await employee.insert()
        team.employees.append(employee)
        await team.save()
        return json({"message": "Employee added successfully", "employee_id": str(employee.id)})

    @post("/teams/{team_id}/applicants")
    @auth()
    async def add_applicant(self, team_id: str, data: FromJSON[ApplicantCreate], request: Request):
        team = await Team.get(team_id)
        if not team:
            return Response(404, content=b"Team not found")
        applicant = Employee(
            full_name=data.value.full_name,
            birth_date=data.value.birth_date,
            birth_place=data.value.birth_place,
            email=data.value.email,
            phone=data.value.phone,
            position=data.value.position,
            astro=data.value.astro,
            role=Role.PENDING,
            team=team,
        )
        await applicant.insert()
        team.employees.append(applicant)
        await team.save()
        return json({"message": "Applicant added successfully", "applicant_id": str(applicant.id)})
