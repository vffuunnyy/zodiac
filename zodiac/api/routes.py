from fastapi import APIRouter, Depends, HTTPException
from passlib.hash import bcrypt

from zodiac.api.auth import (
    AuthRequest,
    AuthResponse,
    authenticate_user,
    create_access_token,
    get_current_user,
)
from zodiac.entities.db.employee import Employee
from zodiac.entities.db.team import Team
from zodiac.entities.db.user import User
from zodiac.entities.dto.astro import AstroShit
from zodiac.entities.dto.auth import (
    UserCreateRequest,
    UserCreateResponse,
)
from zodiac.entities.dto.member import (
    AddMemberRequest,
    AddMemberResponse,
    GetMemberResponse,
    MemberDto,
)
from zodiac.entities.dto.team import TeamCreateRequest, TeamCreateResponse, TeamDto, TeamGetResponse
from zodiac.entities.enums.roles import Role
from zodiac.services.astrology import AstroChart
from zodiac.services.geo import get_coordinates_by_city_name


auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/register", response_model=UserCreateResponse)
async def register(data: UserCreateRequest) -> UserCreateResponse:
    existing_user = await User.find_one(User.email == data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=data.email,
        password=bcrypt.hash(data.password),
        full_name=data.full_name,
    )
    await user.insert()
    return UserCreateResponse(success=True, message="User created successfully")


@auth_router.post("/login", response_model=AuthResponse)
async def login(data: AuthRequest) -> AuthResponse:
    user = await authenticate_user(data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token(str(user.id))
    return AuthResponse(success=True, access_token=access_token)


teams_router = APIRouter(prefix="/teams", tags=["Teams"])


@teams_router.post("/create", response_model=TeamCreateResponse)
async def create_team(
    data: TeamCreateRequest, current_user: User = Depends(get_current_user)
) -> TeamCreateResponse:
    team = Team(
        name=data.name,
        description=data.description,
        employees=[],
    )
    await team.insert()
    return TeamCreateResponse(success=True, id=str(team.id), message="Team created successfully")


@teams_router.get("", response_model=list[TeamDto])
async def list_teams(
    limit: int = 30,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
) -> list[TeamDto]:
    teams = await Team.find({}, fetch_links=True, limit=limit, skip=offset).to_list()
    return [
        TeamDto(
            id=str(team.id),
            name=team.name,
            description=team.description,
        )
        for team in teams
    ]


@teams_router.get("/{team_id}", response_model=TeamGetResponse)
async def get_team(team_id: str, current_user: User = Depends(get_current_user)) -> TeamGetResponse:
    team = await Team.get(team_id, fetch_links=True)
    if not team:
        return TeamGetResponse(success=False)
    team_members = team.employees or []
    astro_charts = {}
    for member in team_members:
        astro_chart = AstroChart(
            birth_time=member.birth_date,
            latitude=member.birth_place.latitude,
            longitude=member.birth_place.longitude,
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
            astro=AstroShit(
                personal_traits=member.personal_traits,
                compatibility=compatibility,
            ),
        )
        if member.role == Role.EMPLOYEE:
            employees.append(data)
        elif member.role == Role.PENDING:
            applicants.append(data)
    return TeamGetResponse(
        success=True,
        team=TeamDto(
            id=str(team.id),
            name=team.name,
            description=team.description,
            employees=employees,
            applicants=applicants,
        ),
    )


members_router = APIRouter(prefix="/members", tags=["Members"])


@members_router.post("/{team_id}/create", response_model=AddMemberResponse)
async def add_employee(
    team_id: str,
    data: AddMemberRequest,
    current_user: User = Depends(get_current_user),
) -> AddMemberResponse:
    team = await Team.get(team_id)
    if not team:
        return AddMemberResponse(success=False, message="Team not found")
    place = data.birth_place.name
    data.birth_place.latitude, data.birth_place.longitude = get_coordinates_by_city_name(place)

    astro_chart = AstroChart(
        birth_time=data.birth_date,
        latitude=data.birth_place.latitude,
        longitude=data.birth_place.longitude,
    )
    employee = Employee(
        full_name=data.full_name,
        birth_date=data.birth_date,
        birth_place=data.birth_place,
        email=data.email,
        phone=data.phone,
        position=data.position,
        personal_traits=astro_chart.calculate_personal_traits(),
        role=data.role,
        team=team,
    )
    await employee.insert()
    team.employees.append(employee)
    await team.save()
    return AddMemberResponse(success=True, message="Employee added successfully")


@members_router.get("/{member_id}", response_model=GetMemberResponse)
async def get_member(member_id: str, current_user: User = Depends(get_current_user)):
    member = await Employee.get(member_id, fetch_links=True, with_children=True, nesting_depth=2)
    if not member:
        return GetMemberResponse(success=False)
    chart = AstroChart(
        birth_time=member.birth_date,
        latitude=member.birth_place.latitude,
        longitude=member.birth_place.longitude,
    )
    team_compatibility = chart.calculate_group_compatibility([
        AstroChart(
            birth_time=employee.birth_date,
            latitude=employee.birth_place.latitude,
            longitude=employee.birth_place.longitude,
        )
        for employee in member.team.employees
    ])
    return GetMemberResponse(
        success=True,
        member=MemberDto(
            id=member_id,
            full_name=member.full_name,
            birth_date=member.birth_date,
            birth_place=member.birth_place,
            email=member.email,
            phone=member.phone,
            position=member.position,
            astro=AstroShit(
                planets=chart.planets,
                houses=chart.houses,
                personal_traits=member.personal_traits,
                compatibility=team_compatibility,
            ),
        ),
    )
