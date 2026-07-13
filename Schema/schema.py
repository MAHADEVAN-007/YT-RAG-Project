from pydantic import BaseModel, EmailStr, Field, ConfigDict

# User Data Schema ->
class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr = Field(max_length=50)

# Creating user ->
class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserPublic(BaseModel):
    model_conifg= ConfigDict(from_attributes=True)
    id: int
    username: str
    img_file: str | None
    img_path: str

class UserPrivate(UserPublic):
    email: EmailStr

class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=50)





