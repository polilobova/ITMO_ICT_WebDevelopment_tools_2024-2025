from sqlmodel import Session, select
from models import User, Transaction, Category, Budget, Goal, TransactionCategoryLink
from typing import List, Optional
from passlib.context import CryptContext
from sqlalchemy.orm import selectinload


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.exec(select(User).where(User.email == email)).first()

def create_user(db: Session, username: str, email: str, password: str) -> User:
    hashed_password = pwd_context.hash(password)
    db_user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_category(db: Session, name: str) -> Category:
    category = Category(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def get_categories(db: Session) -> List[Category]:
    return db.exec(select(Category)).all()

def get_category_by_id(db: Session, category_id: int) -> Optional[Category]:
    return db.get(Category, category_id)

def update_category(db: Session, category_id: int, name: str) -> Optional[Category]:
    category = db.get(Category, category_id)
    if not category:
        return None
    category.name = name
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def delete_category(db: Session, category_id: int):
    category = db.get(Category, category_id)
    if category:
        db.delete(category)
        db.commit()


def create_transaction(db: Session, user_id: int, amount: float, is_income: bool, description: Optional[str], category_ids: List[int]) -> Transaction:
    transaction = Transaction(amount=amount, is_income=is_income, description=description, user_id=user_id)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    for cat_id in category_ids:
        link = TransactionCategoryLink(transaction_id=transaction.id, category_id=cat_id)
        db.add(link)
    db.commit()
    db.refresh(transaction)
    return transaction

def get_transactions_for_user(db: Session, user_id: int) -> List[Transaction]:
    return db.exec(
        select(Transaction)
        .where(Transaction.user_id == user_id)
        .options(selectinload(Transaction.categories))
    ).all()

def get_transaction_by_id(db: Session, transaction_id: int) -> Optional[Transaction]:
    stmt = (
        select(Transaction)
        .where(Transaction.id == transaction_id)
        .options(selectinload(Transaction.categories))
    )
    return db.exec(stmt).first()

def delete_transaction(db: Session, transaction_id: int):
    transaction = get_transaction_by_id(db, transaction_id)
    if transaction:
        db.delete(transaction)
        db.commit()

def update_transaction(db: Session, transaction_id: int, amount: float, is_income: bool, description: Optional[str], category_ids: List[int]) -> Optional[Transaction]:
    transaction = get_transaction_by_id(db, transaction_id)
    if not transaction:
        return None
    transaction.amount = amount
    transaction.is_income = is_income
    transaction.description = description

    db.exec(delete(TransactionCategoryLink).where(TransactionCategoryLink.transaction_id == transaction_id))
    db.commit()
    for cat_id in category_ids:
        link = TransactionCategoryLink(transaction_id=transaction_id, category_id=cat_id)
        db.add(link)
    db.commit()

    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def create_budget(db: Session, user_id: int, month: str, limit: float, category_id: int) -> Budget:
    budget = Budget(user_id=user_id, month=month, limit=limit, category_id=category_id)
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget

def get_budgets_for_user(db: Session, user_id: int) -> List[Budget]:
    return db.exec(select(Budget).where(Budget.user_id == user_id)).all()

def get_budget_by_id(db: Session, budget_id: int) -> Optional[Budget]:
    return db.get(Budget, budget_id)

def update_budget(db: Session, budget_id: int, limit: float) -> Optional[Budget]:
    budget = get_budget_by_id(db, budget_id)
    if not budget:
        return None
    budget.limit = limit
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget

def delete_budget(db: Session, budget_id: int):
    budget = get_budget_by_id(db, budget_id)
    if budget:
        db.delete(budget)
        db.commit()


def create_goal(db: Session, user_id: int, title: str, target_amount: float, deadline: Optional[str]) -> Goal:
    goal = Goal(user_id=user_id, title=title, target_amount=target_amount, deadline=deadline)
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal

def get_goals_for_user(db: Session, user_id: int) -> List[Goal]:
    return db.exec(select(Goal).where(Goal.user_id == user_id)).all()

def get_goal_by_id(db: Session, goal_id: int) -> Optional[Goal]:
    return db.get(Goal, goal_id)

def update_goal(db: Session, goal_id: int, current_amount: float) -> Optional[Goal]:
    goal = get_goal_by_id(db, goal_id)
    if not goal:
        return None
    goal.current_amount = current_amount
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal

def delete_goal(db: Session, goal_id: int):
    goal = get_goal_by_id(db, goal_id)
    if goal:
        db.delete(goal)
        db.commit()