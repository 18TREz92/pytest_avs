import pytest
from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.deposit_account_request import DepositAccountRequest
from sqlalchemy.orm import Session
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.generators.model_generator import RandomModelGenerator


@pytest.mark.api_sen
class TestDepositAccount:
    # Позитивные проверки:
    def test_deposit_account_valid(self, db_session: Session, api_manager: ApiManager,
                                   create_user_request: CreateUserRequest,
                                   create_account_response: CreateAccountResponse):

        account_id = create_account_response.id
        first_amount = RandomModelGenerator.generate_deposit_amount()
        second_amount = RandomModelGenerator.generate_deposit_amount()

        # Первое пополнение
        first_response = api_manager.user_steps.deposit_account(
            create_user_request,
            DepositAccountRequest(
                accountId=account_id,
                amount=first_amount
            )
        )

        assert first_response.id == account_id, 'После первого пополнения в ответе указан неверный счёт'
        assert first_response.balance == create_account_response.balance + first_amount, 'Баланс в ответе API не увеличился на сумму первого пополнения'
        # Второе пополнение того же счёта
        second_response = api_manager.user_steps.deposit_account(
            create_user_request,
            DepositAccountRequest(
                accountId=account_id,
                amount=second_amount
            )
        )

        expected_balance = (create_account_response.balance + first_amount + second_amount)

        assert second_response.id == account_id, 'После второго пополнения в ответе указан неверный счёт'
        assert second_response.balance == expected_balance, 'Баланс в ответе API не учитывает оба пополнения'

        # Проверяем итоговый баланс в БД
        account_from_db = Account.get_account_by_id(db_session, account_id)

        assert (account_from_db is not None and account_from_db.balance == expected_balance), 'Счёт не найден в БД или его баланс не учитывает оба пополнения'

    # Негативные проверки:
    @pytest.mark.parametrize(
        "amount",
        [999.99, 9000.01]
    )
    def test_deposit_account_invalid(self, db_session: Session, amount: float, api_manager: ApiManager,
                                     create_user_request: CreateUserRequest,
                                     create_account_response: CreateAccountResponse):

        # Пытаемся пополнить счёт на недопустимую сумму
        deposit_account_request = DepositAccountRequest(accountId=create_account_response.id,amount=amount)

        api_manager.user_steps.deposit_invalid_account(create_user_request, deposit_account_request)

        # Проверяем, что отклонённое пополнение не изменило баланс
        account_from_db = Account.get_account_by_id(db_session, create_account_response.id)

        assert (account_from_db is not None and account_from_db.balance == create_account_response.balance), 'Счёт не найден в БД или его баланс изменился после отклонённого пополнения'