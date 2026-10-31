import pytest
from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateCreditSecretRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest
from sqlalchemy.orm import Session
from src.main.api.db.crud.credit_crud import CreditCrudDb as Credit
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.utils import calculate_initial_credit_balance



@pytest.mark.api_sen
class TestRepayCredit:
    # Позитивные проверки:
    def test_repay_credit_valid(self, db_session: Session, api_manager: ApiManager,
                                create_credit_secret_request: CreateCreditSecretRequest, create_credit_response):

        # Погашаем кредит единовременно на всю сумму
        credit_repay_response = api_manager.user_steps.repay_credit(
            create_credit_secret_request,
            CreditRepayRequest(
                creditId=create_credit_response.creditId,
                accountId=create_credit_response.id,
                amount=create_credit_response.amount
            )
        )

        assert credit_repay_response.amountDeposited == create_credit_response.amount, 'Сумма погашения в ответе API не совпадает с переданной'

        credit_from_db = Credit.get_credit_by_id(db_session, create_credit_response.creditId)

        assert (credit_from_db is not None and credit_from_db.balance == 0), 'Кредит не найден в БД или его баланс после полного погашения не равен 0'


    # Негативные проверки:
    def test_repay_credit_invalid(self, db_session: Session, api_manager: ApiManager,
                                  create_credit_secret_request: CreateCreditSecretRequest, create_credit_response):

        api_manager.user_steps.repay_invalid_credit(
            create_credit_secret_request,
            CreditRepayRequest(
                creditId=create_credit_response.creditId,
                accountId=create_credit_response.id,
                amount=RandomModelGenerator.generate_partial_repay_amount(
                    create_credit_response.amount
                )
            )
        )

        credit_from_db = Credit.get_credit_by_id(db_session, create_credit_response.creditId)

        assert (
                credit_from_db is not None
                and credit_from_db.balance == calculate_initial_credit_balance(
            create_credit_response.amount
        )
        ), "Кредит не найден в БД или его баланс изменился после отклонённого погашения"