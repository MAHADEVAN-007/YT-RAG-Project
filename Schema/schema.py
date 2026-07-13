from pydantic import BaseModel, EmailStr, Field, ConfigDict

# User Data Schema ->
class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr = Field(max_length=50)

# Creating user ->
class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserPublic(BaseModel):
    model_config= ConfigDict(from_attributes=True)
    id: int
    username: str
    img_file: str | None
    img_path: str

class UserPrivate(UserPublic):
    email: EmailStr

class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=50)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(max_length=50)

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)

class TranscriptSegment(BaseModel):
    text: str
    start: float
    duration: float

class YTTranscriptRequest(BaseModel):
    url: str

class YTTranscriptResponse(BaseModel):
    video_id: str
    title: str
    segments: list[TranscriptSegment]
    full_text: str


    