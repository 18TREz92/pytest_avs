import pytest
from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.deposit_account_request import DepositAccountRequest
from sqlalchemy.orm import Session
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.db.crud.transaction_crud import TransactionCrudDb as Transaction


@pytest.mark.api_sen
class TestDepositAccount:
    # Позитивные проверки:
    def test_deposit_account_valid(self, db_session: Session, api_manager: ApiManager,
                                   create_user_request: CreateUserRequest,
                                   create_account_response: CreateAccountResponse):
        # Проверяем созданный фикстурой счёт
        assert create_account_response.balance == 0
        assert create_account_response.id is not None

        account_id = create_account_response.id
        start_balance = create_account_response.balance

        # Пополнение счёта на минимальную сумму
        min_amount = 1000

        deposit_account_request = DepositAccountRequest(accountId=account_id, amount=min_amount)
        deposit_response = api_manager.user_steps.deposit_account(create_user_request, deposit_account_request)

        assert deposit_response.id == account_id
        assert deposit_response.balance == start_balance + min_amount

        # Проверяем сохранённый баланс после первого пополнения
        account_from_db = Account.get_account_by_id(db_session, account_id)

        assert account_from_db is not None, "Счёт не найден в БД"
        assert account_from_db.balance == start_balance + min_amount, 'В БД неверный баланс после пополнения на минимальную сумму'
        new_balance = deposit_response.balance

        # Проверяем запись первого пополнения
        transactions_from_db = Transaction.get_transactions_by_to_account_id(db_session, account_id)

        assert len(transactions_from_db) == 1, 'После первого пополнения в БД должна быть ровно одна операция'

        first_transaction = transactions_from_db[0]

        assert first_transaction.to_account_id == account_id
        assert first_transaction.from_account_id is None
        assert first_transaction.credit_id is None
        assert first_transaction.amount == min_amount
        assert first_transaction.transaction_type == "deposit"
        assert first_transaction.created_at is not None

        # Пополнение того же счёта на максимальную сумму
        max_amount = 9000

        deposit_account_request = DepositAccountRequest(accountId=account_id, amount=max_amount)
        deposit_response = api_manager.user_steps.deposit_account(create_user_request, deposit_account_request)

        assert deposit_response.id == account_id
        assert deposit_response.balance == new_balance + max_amount

        # Проверяем сохранённый баланс после второго пополнения
        account_from_db = Account.get_account_by_id(db_session, account_id)

        assert account_from_db is not None, "Счёт не найден в БД"
        assert account_from_db.balance == new_balance + max_amount, 'В БД неверный баланс после пополнения на максимальную сумму'

        # Проверяем записи после второго пополнения
        transactions_from_db = Transaction.get_transactions_by_to_account_id(db_session, account_id)

        assert len(transactions_from_db) == 2, 'После двух пополнений в БД должны быть ровно две операции'

        assert transactions_from_db[0].amount == min_amount

        second_transaction = transactions_from_db[1]

        assert second_transaction.to_account_id == account_id
        assert second_transaction.from_account_id is None
        assert second_transaction.credit_id is None
        assert second_transaction.amount == max_amount
        assert second_transaction.transaction_type == "deposit"
        assert second_transaction.created_at is not None

    # Негативные проверки:
    @pytest.mark.parametrize(
        "amount",
        [999.99, 9000.01]
    )
    def test_deposit_account_invalid(self, db_session: Session, amount: float, api_manager: ApiManager,
                                     create_user_request: CreateUserRequest,
                                     create_account_response: CreateAccountResponse):
        # Проверяем созданный фикстурой счёт
        assert create_account_response.balance == 0
        assert create_account_response.id is not None

        account_id = create_account_response.id

        # Проверяем состояние счёта в БД до запроса
        account_from_db = Account.get_account_by_id(db_session, account_id)

        assert account_from_db is not None, "Счёт не найден в БД"
        assert account_from_db.balance == 0

        start_balance = account_from_db.balance

        transactions_before = Transaction.get_transactions_by_to_account_id(db_session, account_id)
        assert transactions_before == [], 'У нового счёта не должно быть входящих операций'

        # Пытаемся пополнить счёт на недопустимую сумму
        deposit_account_request = DepositAccountRequest(accountId=account_id, amount=amount)
        api_manager.user_steps.deposit_invalid_account(create_user_request, deposit_account_request)

        # Проверяем, что баланс не изменился
        account_from_db = Account.get_account_by_id(db_session, account_id)

        assert account_from_db is not None, 'После отказа счёт исчез из БД'
        assert account_from_db.balance == start_balance, 'После отклонённого пополнения изменился баланс в БД'

        # Проверяем, что операция не сохранилась
        transactions_after = Transaction.get_transactions_by_to_account_id(db_session, account_id)
        assert transactions_after == [], 'Отклонённое пополнение сохранилось в БД как операция'
