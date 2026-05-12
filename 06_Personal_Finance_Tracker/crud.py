from database import SessionLocal, Transaction
from datetime import date

# ---------- CREATE ----------
def add_transaction(amount, category, type_, description=""):
    session = SessionLocal()
    transaction = Transaction(
        amount=amount,
        category=category,
        type=type_,
        description=description,
        date=date.today()
    )
    session.add(transaction)
    session.commit()
    session.close()

# ---------- READ ----------
def get_all_transactions():
    session = SessionLocal()
    transactions = session.query(Transaction).all()
    session.close()
    return transactions

# ---------- UPDATE ----------
def update_transaction(transaction_id, amount=None, category=None, description=None):
    session = SessionLocal()
    transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    if transaction:
        if amount is not None:
            transaction.amount = amount
        if category is not None:
            transaction.category = category
        if description is not None:
            transaction.description = description
        session.commit()
    
    session.close()

# ---------- DELETE ----------
def delete_transaction(transaction_id):
    session = SessionLocal()
    transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    if transaction:
        session.delete(transaction)
        session.commit()
    
    session.close()