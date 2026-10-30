import pytest
from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateCreditSecretRequest
from src.main.api.models.credit_request_request import CreditRequestRequest
from sqlalchemy.orm import Session
from src.main.api.db.crud.account_crud import AccountCrudDb as Account


@pytest.mark.api_sen
class TestRequestCredit:
    # Позитивные проверки:
    def test_request_credit_valid(self, db_session: Session, api_manager: ApiManager,
                                  create_credit_secret_request: CreateCreditSecretRequest,
                                  create_credit_account_response):

        amount = RandomModelGenerator.generate_credit_amount()
        term_months = RandomModelGenerator.generate_credit_term_months()

        credit_request = CreditRequestRequest(
            accountId=create_credit_account_response.id,
            amount=amount,
            termMonths=term_months
        )

        credit_response = api_manager.user_steps.request_credit(create_credit_secret_request, credit_request)

        expected_balance = create_credit_account_response.balance + amount

        assert credit_response.balance == expected_balance, 'Баланс в ответе API не увеличился на сумму кредита'

        account_from_db = Account.get_account_by_id(db_session, create_credit_account_response.id)

        assert (account_from_db is not None and account_from_db.balance == expected_balance), 'Счёт не найден в БД или его баланс не увеличился на сумму кредита'


    # Негативные проверки: сумма ниже минимума и выше максимума.

    @pytest.mark.parametrize(
        "amount",
        [4999.99, 15000.01]
    )
    def test_request_credit_invalid(self, db_session: Session, amount: float, api_manager: ApiManager,
                                    create_credit_secret_request: CreateCreditSecretRequest,
                                    create_credit_account_response):
        term_months = RandomModelGenerator.generate_credit_term_months()

        credit_request = CreditRequestRequest(
            accountId=create_credit_account_response.id,
            amount=amount,
            termMonths=term_months
        )

        api_manager.user_steps.request_invalid_credit(create_credit_secret_request, credit_request)

        account_from_db = Account.get_account_by_id(db_session, create_credit_account_response.id)

        assert (account_from_db is not None and account_from_db.balance == create_credit_account_response.balance), 'Счёт не найден в БД или его баланс изменился после отклонённой выдачи кредита'