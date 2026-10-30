from sqlalchemy.orm import Session
from src.main.api.db.models.account_table import Account


class AccountCrudDb:
    @staticmethod
    def get_account_by_id(db: Session, account_id: int) -> Account | None:
        return (
            db.query(Account)
            .populate_existing()
            .filter_by(id=account_id)
            .first()
        )

    @staticmethod
    def delete_account(db: Session, account_id: int) -> None:
        account = db.query(Account).filter_by(id=account_id).first()
        if account:
            db.delete(account)
            db.commit()

    @staticmethod
    def get_accounts_by_user_id(db: Session, user_id: int) -> list[Account]:
        return (
            db.query(Account)
            .filter_by(user_id=user_id)
            .order_by(Account.id)
            .all()
        )

