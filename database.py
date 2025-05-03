from typing import Optional
import asyncpg

from schemas import User, UserDb, UserSignup
from security import create_password_hash
from config import settings

class Postgres:
    def __init__(self, database_url: str):
        self.database_url = database_url

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.database_url)

    async def disconnect(self):
        await self.pool.close()

database = Postgres(settings.database_url)

async def get_user_by_email(email: str) -> Optional[UserDb]:
    query = """
        SELECT id, first_name, last_name, email, password_hash
        FROM users
        WHERE email = $1
    """
    async with database.pool.acquire() as connection:
        row = await connection.fetchrow(query, email)
        if not row:
            return None
        user_db = UserDb(
            id=str(row['id']),
            first_name=row['first_name'],
            last_name=row['last_name'],
            email=row['email'],
            hashed_password=row['password_hash'],
        )
        return user_db

async def get_user_by_id(id: str) -> Optional[User]:
    query = """
        SELECT id, first_name, last_name, email
        FROM users
        WHERE id = $1
    """
    async with database.pool.acquire() as connection:
        row = await connection.fetchrow(query, int(id))  # Passa o ID como parâmetro
    if not row:
        return None
    user = User(
        id=str(row['id']),
        first_name=row['first_name'],
        last_name=row['last_name'],
        email=row['email'],
    )
    return user

async def add_user_db(user_signup: UserSignup) -> User:    
    query = """
        INSERT INTO users (first_name, last_name, email, password_hash)
        VALUES ($1, $2, $3, $4)
        RETURNING id, first_name, last_name, email
    """    
    hashed_password = create_password_hash(user_signup.password)
    async with database.pool.acquire() as connection:
        row = await connection.fetchrow(query, user_signup.first_name, user_signup.last_name, user_signup.email, hashed_password)        
        user = User(
            id=str(row['id']),
            first_name=row['first_name'],
            last_name=row['last_name'],
            email=row['email'],        
        )
        return user
    
async def change_user_password(user_id: int, new_password: str) -> None:    
    query = "UPDATE users SET password_hash = $2 WHERE id = $1"    
    hashed_password = create_password_hash(new_password)
    async with database.pool.acquire() as connection:
        row = await connection.execute(query, user_id, hashed_password) 
        
async def delete_user(user_id: int) -> None:    
    query = "DELETE FROM users WHERE id = $1"    
    async with database.pool.acquire() as connection:
        await connection.execute(query, user_id)        
        

