import aiohttp
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlmodel import select
from app.celery_app import celery_app
from auth.auth import authenticate_user, create_access_token, get_current_user
from models.models import User, Task, TaskTag, TimeLog, Tag
from database.connection import init_db, get_session
from models.schemas import *
from auth.security import *

router = APIRouter()

@router.post("/parse")
async def parse(parse_request: ParseRequest):
    parser_url = "http://parser_app:8001/parse"
    async with aiohttp.ClientSession() as client:
        response = await client.post(parser_url, json=parse_request.model_dump(), timeout=15)
        response.raise_for_status()
        return await response.json()


@router.post("/parse-queue")
def start_parse(request: ParseRequest):
    task = celery_app.send_task("app.tasks.parse_url_task", args=[request.urls])
    return {"task_id": task.id}


@router.get("/status/{task_id}")
def check_status(task_id: str):
    result = celery_app.AsyncResult(task_id)
    return {"status": result.status, "result": result.result}

@router.post("/register", response_model=UserRead)
def register(user: UserCreate, session: Session = Depends(get_session)):
    if session.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_pwd = hash_password(user.password)
    db_user = User(username=user.username, email=user.email, password=hashed_pwd)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
def login(user: UserLogin, session: Session = Depends(get_session)):
    auth_user = authenticate_user(session, user.username, user.password)
    if not auth_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": auth_user.username})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserRead)
def get_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# Получить список всех пользователей
@router.get("/users", response_model=list[UserRead])
def list_users(session: Session = Depends(get_session)):
    return session.query(User).all()

@router.post("/change-password")
def change_password(data: ChangePassword, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if not verify_password(data.old_password, user.password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    user.password = hash_password(data.new_password)
    session.add(user)
    session.commit()
    return {"message": "Password changed successfully"}

# Получить одного пользователя по ID
@router.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Создать нового пользователя
@router.post("/users", response_model=UserRead)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    db_user = User(username=user.username, email=user.email, password=hash_password(user.password))
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

# Удалить пользователя
@router.delete("/users/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"status": 200, "message": "User deleted"}

# Получить все задачи пользователя
@router.get("/users/{user_id}/tasks", response_model=list[TaskRead])
def get_user_tasks(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return session.exec(select(Task).where(Task.user_id == user_id)).all()

# Добавить новую задачу пользователю
@router.post("/users/{user_id}/tasks", response_model=TaskRead)
def create_task(user_id: int, task: Task, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    task.user_id = user_id
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

# Удалить задачу пользователя
@router.delete("/users/{user_id}/tasks/{task_id}")
def delete_task(user_id: int, task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"status": 200, "message": "Task deleted"}

# Обновить задачу
@router.patch("/users/{user_id}/tasks/{task_id}", response_model=TaskRead)
def update_task(user_id: int, task_id: int, updated_task: Task, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = updated_task.dict(exclude_unset=True)
    for key, value in task_data.items():
        setattr(task, key, value)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task

# Получить список всех тегов
@router.get("/tags", response_model=list[TagRead])
def get_all_tags(session: Session = Depends(get_session)):
    return session.exec(select(Tag)).all()

# Получить конкретный тег
@router.get("/tags/{tag_id}", response_model=TagRead)
def get_tag(tag_id: int, session: Session = Depends(get_session)):
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag

# Создать новый тег
@router.post("/tags", response_model=TagRead)
def create_tag(tag: Tag, session: Session = Depends(get_session)):
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag

# Обновить тег (частично)
@router.patch("/tags/{tag_id}", response_model=TagRead)
def update_tag(tag_id: int, updated_tag: Tag, session: Session = Depends(get_session)):
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    tag_data = updated_tag.dict(exclude_unset=True)
    for key, value in tag_data.items():
        setattr(tag, key, value)

    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag

# Удалить тег
@router.delete("/tags/{tag_id}")
def delete_tag(tag_id: int, session: Session = Depends(get_session)):
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    session.delete(tag)
    session.commit()
    return {"status": 200, "message": "Tag deleted"}

# Добавление тега к задаче с указанием уровня важности
@router.post("/tasks/{task_id}/tags/{tag_id}", response_model=TaskTagRead)
def add_tag_to_task(task_id: int, tag_id: int, importance_level: int = 1, session: Session = Depends(get_session)):
    existing = session.get(TaskTag, (task_id, tag_id))
    if existing:
        raise HTTPException(status_code=400, detail="Tag already assigned to task")
    task_tag = TaskTag(task_id=task_id, tag_id=tag_id, importance_level=importance_level)
    session.add(task_tag)
    session.commit()
    session.refresh(task_tag)
    return task_tag

# Обновление уровня важности для уже назначенного тега
@router.patch("/tasks/{task_id}/tags/{tag_id}", response_model=TaskTagRead)
def update_tag_on_task(task_id: int, tag_id: int, importance_level: int, session: Session = Depends(get_session)):
    task_tag = session.get(TaskTag, (task_id, tag_id))
    if not task_tag:
        raise HTTPException(status_code=404, detail="Tag not assigned to task")
    task_tag.importance_level = importance_level
    session.add(task_tag)
    session.commit()
    session.refresh(task_tag)
    return task_tag

# Удаление тега из задачи
@router.delete("/tasks/{task_id}/tags/{tag_id}")
def remove_tag_from_task(task_id: int, tag_id: int, session: Session = Depends(get_session)):
    task_tag = session.get(TaskTag, (task_id, tag_id))
    if not task_tag:
        raise HTTPException(status_code=404, detail="Tag not assigned to task")
    session.delete(task_tag)
    session.commit()
    return {"status": 200, "message": "Tag removed from task"}

# Получение всех тегов, привязанных к задаче, с уровнем важности
@router.get("/tasks/{task_id}/tags", response_model=list[TagReadWithImportanceLevel])
def get_tags_for_task(task_id: int, session: Session = Depends(get_session)):
    stmt = select(TaskTag, Tag).where(TaskTag.task_id == task_id, TaskTag.tag_id == Tag.tag_id)
    results = session.exec(stmt).all()
    return [
        TagReadWithImportanceLevel(
            tag_id=tag.tag_id,
            name=tag.name,
            importance_level=tt.importance_level,
            created_at=tt.created_at
        )
        for tt, tag in results
    ]