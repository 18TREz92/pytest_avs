import pytest
from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.deposit_account_request import DepositAccountRequest
from sqlalchemy.orm import Session
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.utils import calculate_balance_after_deposit


@pytest.mark.api_sen
class TestDepositAccount:
    # Позитивные проверки:
    def test_deposit_account_valid(self, db_session: Session, api_manager: ApiManager,
                                   create_user_request: CreateUserRequest,
                                   create_account_response: CreateAccountResponse):

        amount = RandomModelGenerator.generate_deposit_amount()

        response = api_manager.user_steps.deposit_account(
            create_user_request,
            DepositAccountRequest(
                accountId=create_account_response.id,
                amount=amount
            )
        )

        expected_balance = calculate_balance_after_deposit(create_account_response.balance, amount)

        assert response.id == create_account_response.id, 'После пополнения в ответе указан неверный счёт'
        assert response.balance == expected_balance,'Баланс в ответе API не увеличился на сумму пополнения'

        account_from_db = Account.get_account_by_id(db_session, create_account_response.id)

        assert (account_from_db is not None and account_from_db.balance == expected_balance), 'Счёт не найден в БД или его баланс не увеличился на сумму пополнения'


    # Негативные проверки:
    @pytest.mark.parametrize(
        "amount",
        [999.99, 9000.01]
    )
    def test_deposit_account_invalid(self, db_session: Session, amount: float, api_manager: ApiManager,
                                     create_user_request: CreateUserRequest,
                                     create_account_response: CreateAccountResponse):

        # Пытаемся пополнить счёт на недопустимую сумму
        api_manager.user_steps.deposit_invalid_account(create_user_request, DepositAccountRequest(accountId=create_account_response.id,amount=amount))

        # Проверяем, что отклонённое пополнение не изменило баланс
        account_from_db = Account.get_account_by_id(db_session, create_account_response.id)

        assert (account_from_db is not None and account_from_db.balance == create_account_response.balance), 'Счёт не найден в БД или его баланс изменился после отклонённого пополнения'