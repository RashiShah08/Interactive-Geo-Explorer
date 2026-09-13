from pydantic import BaseModel, Field


class Credentials(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=200)


class AuthResult(BaseModel):
    ok: bool
    message: str = ""
    username: str | None = None


class PlaceOut(BaseModel):
    key: str
    title: str
    description: str
    image_url: str
    lat: float
    lon: float
    category: str


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatIn(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=40)


class Citation(BaseModel):
    key: str
    title: str
    atlas: str
    category: str


class ChatOut(BaseModel):
    ok: bool
    reply: str = ""
    message: str = ""
    citations: list[Citation] = []
