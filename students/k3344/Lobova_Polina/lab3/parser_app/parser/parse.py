from pydantic import BaseModel


class ParseRequest(BaseModel):
    urls: list[str]