"""Application startup and configuration."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.core.api.assignment.router import router as assignment_router
from apps.core.api.authentication.router import router as auth_router
from apps.core.api.authorization.middleware import AuthorizationMiddleware
from apps.core.api.authorization.router import router as authorization_router
from apps.core.api.role.router import router as role_router
from apps.core.api.transaction.router import router as transaction_router
from apps.core.api.user.router import router as user_router
from apps.ia.api.chat.router import router as chat_router

app = FastAPI(
    title="FastAPI Starter faster than ever",
    description="FastAPI Starter",
    version="0.1.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_tags=[
        {
            "name": "Users",
            "description": "Operations with users",
        },
        {
            "name": "Auth",
            "description": "Operations with authentication",
        },
        {
            "name": "Transactions",
            "description": "Operations with transactions",
        },
        {
            "name": "Roles",
            "description": "Operations with roles",
        },
        {
            "name": "Assignments",
            "description": "Operations with assignments",
        },
        {
            "name": "Authorizations",
            "description": "Operations with authorizations",
        },
        {
            "name": "AI Chat",
            "description": "Operations with AI chat and conversation management",
        },
    ],
)


# ----------------------------------
#  APP CORSMiddleware
# ----------------------------------
origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


# ----------------------------------
#  APP MIDDLEWARES
# ----------------------------------
app.add_middleware(AuthorizationMiddleware)

# ----------------------------------
#   APP ROUTERS
# ----------------------------------
app.include_router(user_router, prefix='/users', tags=['Users'])
app.include_router(auth_router, prefix='/auth', tags=['Auth'])
app.include_router(
    transaction_router, prefix='/transaction', tags=['Transactions']
)
app.include_router(role_router, prefix='/role', tags=['Roles'])
app.include_router(
    assignment_router, prefix='/assignment', tags=['Assignments']
)
app.include_router(
    authorization_router, prefix='/authorization', tags=['Authorizations']
)
app.include_router(chat_router, prefix="/chat", tags=["AI Chat"])
# ----------------------------------


@app.get('/')
def read_root():
    """Root endpoint to verify that the API is running."""
    return {'message': 'Welcome to API!'}
