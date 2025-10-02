from fastapi import FastAPI
from parser.parse import ParseRequest
from parser.parser import run_parser
from sqlmodel import select, Session
from parser.models import ParsedTag
from parser.parser import engine

app = FastAPI()

@app.get("/tags")
async def get_parsed_tags():
    with Session(engine) as session:
        tags = session.exec(select(ParsedTag)).all()
        return tags
@app.post("/parse")
async def parse_url(parse_request: ParseRequest):
    print(parse_request.urls)
    print(f"Parsing URLS: {parse_request.urls}")
    await run_parser(parse_request.urls)
    return {"message": "Parsing completed"}