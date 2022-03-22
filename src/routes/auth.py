from os import environ

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from starlette_discord import DiscordOAuthClient

from ..impl.types import Request


class TokenResponse(BaseModel):
    token: str


router = APIRouter(prefix="/auth")
oauth = DiscordOAuthClient(
    client_id=environ["CLIENT_ID"],
    client_secret=environ["CLIENT_SECRET"],
    redirect_uri=environ["BASE_URL"] + "/auth/callback",
)


@router.get("/discord")
async def discord_login() -> RedirectResponse:
    return oauth.redirect()  # type: ignore


@router.get("/callback")
async def oauth_callback(request: Request, code: str) -> RedirectResponse:
    user = await oauth.login(code)  # type: ignore
    await request.state.users.ensure(user.id, user.username, user.discriminator)  # type: ignore
    handoff = await request.state.auth.generate_handoff(user.id)  # type: ignore

    return RedirectResponse(url=f"{environ['DASHBOARD_URL']}/access?handoff={handoff}")


@router.get("/token", response_model=TokenResponse)
async def get_token(request: Request, handoff: str) -> TokenResponse:
    data = await request.state.auth.from_handoff(handoff)

    if not data:
        raise HTTPException(status_code=404, detail="Handoff token not found")

    return TokenResponse(token=data[0])

@router.get("/hi")
async def hi(request: Request) -> dict[str, bool]:
    if not (token := request.headers.get("Authorization")):
        return {
            "success": False,
        }

    valid = await request.state.auth.decode(token)

    if valid is None:
        return {
            "success": False,
        }

    return {
        "success": True,
    }
