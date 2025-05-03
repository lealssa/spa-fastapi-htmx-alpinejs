from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.exceptions import RequestValidationError
from fastapi.templating import Jinja2Templates
from typing import Annotated

from schemas import User, UserLogin, UserSignup, UserDb, UserChangePassword, UserDelete, UserJwt
from database import add_user_db, get_user_by_email, database, change_user_password, delete_user
from security import create_access_token, check_password_hash, NotAuthenticatedError
from dependency import oauth_cookie, get_current_year, current_user_from_jwt
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
     await database.connect()
     yield
     await database.disconnect()

app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory="templates")
templates.env.globals['get_current_year'] = get_current_year

# Exception Handlers

@app.exception_handler(404)
async def custom_404_handler(request, _):
    return RedirectResponse('/404')

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    err: str|list = exc.errors()
    print(err)
    if type(err) is list:
        err = "Verifique o(s) campo(s)"
    headers: dict[str,str] = {'HX-Reswap': 'innerHTML', 'HX-Retarget': '#error-banner'}
    context = {'error': err} 
    return templates.TemplateResponse(request, 'components/_error_banner.html', context=context, headers=headers)

@app.exception_handler(NotAuthenticatedError)
async def not_authenticated_exception_handler(request, exc):    
    return RedirectResponse('/login', status_code=status.HTTP_303_SEE_OTHER)

# Routers

@app.get('/404', response_class=HTMLResponse)
async def not_found(request: Request) -> HTMLResponse:
    headers: dict[str,str] = {'HX-Reswap': 'innerHTML', 'HX-Retarget': '#main-content'}
    return templates.TemplateResponse("pages/404.html", {"request": request}, headers=headers)

@app.get('/', response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(oauth_cookie)) -> HTMLResponse:
    context = {'title': 'Index', 'user': user}    
    return templates.TemplateResponse(request, 'pages/index.html', context=context)

@app.get('/meus-dados', response_class=HTMLResponse)
async def user_data(request: Request, user: User = Depends(oauth_cookie)) -> HTMLResponse:
    context = {'title': 'Meus dados', 'user': user}    
    return templates.TemplateResponse(request, 'pages/user_data.html', context=context)

@app.get('/login', response_model=None)
async def login(request: Request, user_jwt: UserJwt | None = Depends(current_user_from_jwt)) -> HTMLResponse | RedirectResponse:
    if user_jwt:
        return RedirectResponse("/")
    context = {'title': 'Login'}
    return templates.TemplateResponse(request, 'pages/login.html', context=context)

@app.post('/login')
async def user_login(request: Request, user_login: Annotated[UserLogin, Form()]) -> RedirectResponse:
    user_db: UserDb = await get_user_by_email(user_login.email)
    if not user_db or not check_password_hash(user_login.password, user_db.hashed_password):
        raise RequestValidationError('Usuário ou senha inválidos!')
    user_jwt = UserJwt(**user_db.model_dump())
    token: str = create_access_token(user_jwt)
    response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        "access_token",
        f"Bearer {token}",
        samesite="lax",
        expires=settings.expiration_time,
        httponly=True,
        # secure=True,
    )
    return response

@app.get("/logout", response_model=None)
async def logout(request: Request, response: Response) -> RedirectResponse|HTMLResponse:
    response = RedirectResponse("/login")
    response.delete_cookie("access_token")     
    return response

@app.get('/criar-conta', response_model=None)
async def signup(request: Request, user_jwt: UserJwt | None = Depends(current_user_from_jwt)) -> HTMLResponse | RedirectResponse:
    if user_jwt:
        return RedirectResponse("/meus-dados")
    context = {'title': 'Cadastro de usuário'}
    return templates.TemplateResponse(request, 'pages/signup.html', context=context)

@app.post('/criar-conta', response_class=HTMLResponse)
async def add_user(request: Request, user_signup: Annotated[UserSignup, Form()]) -> HTMLResponse:
    if len(user_signup.password) < 6:
        raise RequestValidationError('A senha precisa ter 6 ou mais caracteres.')    
    
    if user_signup.password != user_signup.password_confirm:
        raise RequestValidationError('As senhas não são iguais.')        
    
    if await get_user_by_email(user_signup.email):
        raise RequestValidationError('O usuário já existe.')    
    
    await add_user_db(user_signup)
    return templates.TemplateResponse(request, 'components/_signup_success.html', context={'title': 'Usuário criado!'})

@app.get('/alterar-senha', response_class=HTMLResponse)
async def user_password(request: Request, user: User = Depends(oauth_cookie)) -> HTMLResponse:
    context = {'title': 'Alteração de senha', 'user': user}
    return templates.TemplateResponse(request, 'pages/change_password.html', context=context)

@app.post('/alterar-senha', response_class=HTMLResponse)
async def change_password(request: Request, user_change_password: Annotated[UserChangePassword, Form()], user: User = Depends(oauth_cookie)) -> RedirectResponse:
    if user_change_password.new_password != user_change_password.password_confirm:
        raise RequestValidationError('As senhas não são iguais.')    
    
    user_db = await get_user_by_email(user.email)    
    
    if not check_password_hash(user_change_password.password, user_db.hashed_password):
        raise RequestValidationError('Usuário ou senha inválidos.')  
    
    await change_user_password(int(user.id), user_change_password.new_password)   
     
    return RedirectResponse("/logout", status_code=status.HTTP_303_SEE_OTHER)

@app.get('/deletar-conta', response_class=HTMLResponse)
async def confirm_delete_account(request: Request, user: User = Depends(oauth_cookie)) -> HTMLResponse:
    context = {'title': 'Remoção de conta', 'user': user}
    return templates.TemplateResponse(request, 'pages/delete_account.html', context=context)

@app.post('/deletar-conta', response_class=HTMLResponse)
async def delete_account(request: Request, user_delete: Annotated[UserDelete, Form()], user: User = Depends(oauth_cookie)) -> RedirectResponse:  
    if not user_delete.confirm_delete_account:
        raise RequestValidationError('Aceite os termos.')
    await delete_user(int(user.id))
    return RedirectResponse("/logout", status_code=status.HTTP_303_SEE_OTHER)

@app.get('/_navbar', response_class=HTMLResponse)
async def get_navbar(request: Request, user_jwt: UserJwt | None = Depends(current_user_from_jwt)) -> HTMLResponse:
    context = {'user': user_jwt}
    return templates.TemplateResponse(request, 'components/_navbar.html', context=context)