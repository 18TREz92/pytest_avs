from src.main.api.models.base_model import BaseModel


class CreditRequestRequest(BaseModel):
    accountId: int
    amount: float
    termMonths: int