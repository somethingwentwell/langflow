from sqlmodel import Session
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm

from langflow.services.utils import get_session
from langflow.api.v1.schemas import Token
from langflow.services.auth.utils import (
    authenticate_user,
    create_user_tokens,
    create_refresh_token,
    create_user_longterm_token,
    get_current_active_user,
    get_user_by_username
)

from langflow.services.utils import get_settings_manager

from fastapi import HTTPException  
from fastapi.responses import RedirectResponse
from starlette.requests import Request 
from fastapi.responses import HTMLResponse 
from jose import jwt  
from urllib.parse import urlencode  
import httpx  
import os

HOST = os.environ.get("LANGFLOW_HOST", "localhost")

def get_cb_url(call_type):
    if call_type == "login":
        return f"http://{HOST}/login"
    else:
        return f"http://{HOST}/api/v1/oauth2_callback"

router = APIRouter(tags=["Login"])


@router.post("/login", response_model=Token)
async def login_to_get_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_session),
    # _: Session = Depends(get_current_active_user)
):
    if user := authenticate_user(form_data.username, form_data.password, db):
        return create_user_tokens(user_id=user.id, db=db, update_last_login=True)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/auto_login")
async def auto_login(
    db: Session = Depends(get_session), settings_manager=Depends(get_settings_manager)
):
    if settings_manager.auth_settings.AUTO_LOGIN:
        return create_user_longterm_token(db)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "message": "Auto login is disabled. Please enable it in the settings",
            "auto_login": False,
        },
    )


@router.post("/refresh")
async def refresh_token(
    token: str, current_user: Session = Depends(get_current_active_user)
):
    if token:
        return create_refresh_token(token)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/oauth2", response_class=HTMLResponse)  
async def oauth2(request: Request, call_type: str = Query(..., description="The type of call being made (login/api)")):  
    call_type = request.query_params.get("call_type")
    base_authorization_url = os.environ.get("OAUTH2_AUTH_URL")
    params = {  
        "client_id": os.environ.get("OAUTH2_CLIENT_ID"),  
        "response_type": "code",  
        "redirect_uri": get_cb_url(call_type),  # Replace with your callback URL  
        "scope": os.environ.get("OAUTH2_SCOPE"),  
        "state": call_type,  # Replace with a secure random string  
    }  
    print(params)
    authorization_url = f"{base_authorization_url}?{urlencode(params)}"  
    return RedirectResponse(authorization_url)


@router.get("/oauth2_callback")  
async def callback(request: Request):  
    code = request.query_params.get("code")  
    state = request.query_params.get("state")  
    if not code:  
        raise HTTPException(status_code=400, detail="Missing authorization code")  
  
    token_url = os.environ.get("OAUTH2_TOKEN_URL")
    token_data = {  
        "grant_type": "authorization_code",  
        "client_id": os.environ.get("OAUTH2_CLIENT_ID"),  
        "code": code,  
        "redirect_uri": get_cb_url(state),
        "scope": os.environ.get("OAUTH2_SCOPE"),  
        "client_secret": os.environ.get("OAUTH2_CLIENT_SECRET"), 
    }  
  
    async with httpx.AsyncClient() as client:  
        response = await client.post(token_url, data=token_data)  
  
    if response.status_code != 200:  
        raise HTTPException(status_code=400, detail="Failed to get access token")  
  
    token_response = response.json()  
    return token_response

@router.get("/oauth2_get_user_token")
async def callback(request: Request, db: Session = Depends(get_session), 
                   access_token: str = Query(..., description="The access token from the oauth2_callback"), 
                   id_token: str = Query(..., description="The access token from the oauth2_callback")):
    access_token = request.query_params.get("access_token")
    id_token = request.query_params.get("id_token")

    # Get the unverified claims from the ID token to get the user's email  
    unverified_claims = jwt.get_unverified_claims(id_token)  
    user_email = unverified_claims["email"]  
    user_name = user_email.split('@')[0]

    user = get_user_by_username(db, user_name)

    if not user:
        raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail= user_name + " is not authorized",
                    headers={"WWW-Authenticate": "Bearer"},
                )

    if not user.is_active:
        if not user.last_login_at:
            raise HTTPException(status_code=400, detail="Waiting for approval")
        raise HTTPException(status_code=400, detail="Inactive user")
  
    return create_user_tokens(user_id=user.id, db=db, update_last_login=True) 