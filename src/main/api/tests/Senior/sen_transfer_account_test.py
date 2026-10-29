import pytest
from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.deposit_account_request import DepositAccountRequest
from src.main.api.models.transfer_account_request import TransferAccountRequest
from sqlalchemy.orm import Session
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.db.crud.transaction_crud import TransactionCrudDb as Transaction


@pytest.mark.api_sen
class TestTransferAccount:
    # Позитивные проверки:
    def test_transfer_account_valid(self, db_session: Session, api_manager: ApiManager,
                                    create_user_request: CreateUserRequest, create_two_accounts):
        # Получаем два счёта из фикстуры
        from_account, to_account = create_two_accounts

        assert from_account.balance == 0
        assert from_account.id is not None

        assert to_account.balance == 0
        assert to_account.id is not None

        assert from_account.id != to_account.id

        # Пополняем счёт отправителя
        deposit_amount = 2000

        deposit_account_request = DepositAccountRequest(accountId=from_account.id, amount=deposit_amount)

        deposit_response = api_manager.user_steps.deposit_account(create_user_request, deposit_account_request)

        assert deposit_response.id == from_account.id
        assert deposit_response.balance == from_account.balance + deposit_amount

        # Проверяем подготовленные балансы в БД
        from_account_from_db = Account.get_account_by_id(db_session, from_account.id)
        to_account_from_db = Account.get_account_by_id(db_session, to_account.id)

        assert from_account_from_db is not None, 'Счёт отправителя не найден в БД'
        assert to_account_from_db is not None, 'Счёт получателя не найден в БД'

        assert from_account_from_db.balance == from_account.balance + deposit_amount
        assert to_account_from_db.balance == to_account.balance

        # Сохраняем балансы числами до перевода
        from_balance_before_transfer = from_account_from_db.balance
        to_balance_before_transfer = to_account_from_db.balance

        # Переводим на счёт №2 минимальную сумму
        transfer_amount = 500
        transfer_account_request = TransferAccountRequest(
            fromAccountId=from_account.id,
            toAccountId=to_account.id,
            amount=transfer_amount
        )

        transfer_response = api_manager.user_steps.transfer_account(create_user_request, transfer_account_request)

        assert transfer_response.fromAccountIdBalance == deposit_response.balance - transfer_amount

        # Повторно получаем оба счёта после перевода
        from_account_from_db = Account.get_account_by_id(db_session, from_account.id)
        to_account_from_db = Account.get_account_by_id(db_session, to_account.id)

        assert from_account_from_db is not None, 'После перевода счёт отправителя не найден'
        assert to_account_from_db is not None, 'После перевода счёт получателя не найден'

        assert from_account_from_db.balance == from_balance_before_transfer - transfer_amount, 'В БД неверный баланс отправителя после перевода'
        assert to_account_from_db.balance == to_balance_before_transfer + transfer_amount, 'В БД неверный баланс получателя после перевода'

        # Получаем операции, в которых наш счёт является получателем
        transactions_from_db = Transaction.get_transactions_by_to_account_id(db_session, to_account.id)

        assert len(
            transactions_from_db) == 1, 'После перевода на счёт получателя должна быть записана ровно одна операция'

        transfer_transaction = transactions_from_db[0]

        assert transfer_transaction.from_account_id == from_account.id, 'В операции перевода указан неверный отправитель'
        assert transfer_transaction.to_account_id == to_account.id, 'В операции перевода указан неверный получатель'
        assert transfer_transaction.amount == transfer_amount, 'В БД сохранена неверная сумма перевода'
        assert transfer_transaction.transaction_type == "transfer", 'В БД сохранён неверный тип операции'
        assert transfer_transaction.credit_id is None, 'Перевод между счетами не должен быть связан с кредитом'
        assert transfer_transaction.created_at is not None, 'В БД отсутствует дата создания операции'

    # Негативные проверки
    @pytest.mark.parametrize(
        "transfer_amount",
        [499.99, 10000.01]
    )
    def test_transfer_account_invalid(self, db_session: Session, transfer_amount: float, api_manager: ApiManager,
                                      create_user_request: CreateUserRequest, create_two_accounts):
        # Получаем два счёта из фикстуры
        from_account, to_account = create_two_accounts

        assert from_account.balance == 0
        assert from_account.id is not None

        assert to_account.balance == 0
        assert to_account.id is not None

        assert from_account.id != to_account.id

        # Пополняем счёт отправителя на максимально возможную сумму
        first_amount = 9000
        first_deposit_request = DepositAccountRequest(accountId=from_account.id, amount=first_amount)

        first_deposit_response = api_manager.user_steps.deposit_account(create_user_request, first_deposit_request)

        assert first_deposit_response.id == from_account.id
        assert first_deposit_response.balance == from_account.balance + first_amount

        # Второе пополнение: доводим баланс до 11000
        second_amount = 2000
        second_deposit_request = DepositAccountRequest(accountId=from_account.id, amount=second_amount)

        second_deposit_response = api_manager.user_steps.deposit_account(create_user_request, second_deposit_request)

        assert second_deposit_response.id == from_account.id
        assert second_deposit_response.balance == first_deposit_response.balance + second_amount

        # Проверяем подготовленные балансы в БД
        from_account_from_db = Account.get_account_by_id(db_session, from_account.id)
        to_account_from_db = Account.get_account_by_id(db_session, to_account.id)

        assert from_account_from_db is not None, 'Счёт отправителя не найден в БД'
        assert to_account_from_db is not None, 'Счёт получателя не найден в БД'

        assert from_account_from_db.balance == from_account.balance + first_amount + second_amount, 'В БД неверный баланс отправителя перед переводом'
        assert to_account_from_db.balance == to_account.balance, 'В БД неверный баланс получателя перед переводом'

        # Сохраняем балансы числами до запроса
        from_balance_before_transfer = from_account_from_db.balance
        to_balance_before_transfer = to_account_from_db.balance

        # Запоминаем операции отправителя до запроса
        from_transactions_before = Transaction.get_transactions_by_account_id(db_session, from_account.id)

        assert len(from_transactions_before) == 2, 'У отправителя должны быть две операции подготовительных пополнений'

        from_transaction_ids_before = [transaction.id for transaction in from_transactions_before]

        # Проверяем отсутствие операций у получателя
        to_transactions_before = Transaction.get_transactions_by_account_id(db_session, to_account.id)

        assert to_transactions_before == [], 'У нового счёта получателя не должно быть операций'

        # Пытаемся перевести недопустимую сумму
        transfer_account_request = TransferAccountRequest(
            fromAccountId=from_account.id,
            toAccountId=to_account.id,
            amount=transfer_amount
        )

        api_manager.user_steps.transfer_invalid_account(create_user_request, transfer_account_request)

        # Проверяем балансы после отклонённого перевода
        from_account_from_db = Account.get_account_by_id(db_session, from_account.id)
        to_account_from_db = Account.get_account_by_id(db_session, to_account.id)

        assert from_account_from_db is not None, 'После отказа счёт отправителя не найден'
        assert to_account_from_db is not None, 'После отказа счёт получателя не найден'
        assert from_account_from_db.balance == from_balance_before_transfer, 'После отклонённого перевода изменился баланс отправителя в БД'
        assert to_account_from_db.balance == to_balance_before_transfer, 'После отклонённого перевода изменился баланс получателя в БД'

        # Проверяем, что список операций отправителя не изменился
        from_transactions_after = Transaction.get_transactions_by_account_id(db_session, from_account.id)

        from_transaction_ids_after = [transaction.id for transaction in from_transactions_after]

        assert from_transaction_ids_after == from_transaction_ids_before, 'После отклонённого перевода изменился список операций отправителя'

        # Проверяем, что у получателя не появилось операций
        to_transactions_after = Transaction.get_transactions_by_account_id(db_session, to_account.id)

        assert to_transactions_after == [], 'После отклонённого перевода у получателя появилась операция в БД'
