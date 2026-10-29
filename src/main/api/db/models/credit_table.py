from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from src.main.api.db.base import Base


class Credit(Base):
    __tablename__ = 'credit'
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('account.id'), nullable=False)
    amount = Column(Float, nullable=False)
    term_months = Column(Integer, nullable=False)
    balance = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False)

    def __repr__(self):
        return f'<Credit(id={self.id}, account_id={self.account_id}, amount={self.amount}, term_months={self.term_months}, balance={self.balance}, created_at={self.created_at})>'
