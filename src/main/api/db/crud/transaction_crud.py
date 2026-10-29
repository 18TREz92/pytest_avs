from sqlalchemy import or_
from sqlalchemy.orm import Session
from src.main.api.db.models.transaction_table import Transaction


class TransactionCrudDb:
    @staticmethod
    def get_transactions_by_to_account_id(db: Session, account_id: int) -> list[Transaction]:
        return (
            db.query(Transaction)
            .populate_existing()
            .filter_by(to_account_id=account_id)
            .order_by(Transaction.id)
            .all()
        )

    @staticmethod
    def get_transactions_by_account_id(db: Session, account_id: int) -> list[Transaction]:
        return (
            db.query(Transaction)
            .populate_existing()
            .filter(
                or_(
                    Transaction.to_account_id == account_id,
                    Transaction.from_account_id == account_id
                )
            )
            .order_by(Transaction.id)
            .all()
        )