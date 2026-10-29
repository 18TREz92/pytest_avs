import pytest
from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateCreditSecretRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest
from sqlalchemy.orm import Session
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.db.crud.credit_crud import CreditCrudDb as Credit
from src.main.api.db.crud.transaction_crud import TransactionCrudDb as Transaction


@pytest.mark.api_sen
class TestRepayCredit:
    # Позитивные проверки:
    def test_repay_credit_valid(self, db_session: Session, api_manager: ApiManager,
                                create_credit_secret_request: CreateCreditSecretRequest, create_credit_response):
        # Погашаем кредит единовременно на всю сумму
        repay_amount = create_credit_response.amount

        account_id = create_credit_response.id
        credit_id = create_credit_response.creditId

        # Проверяем состояние счёта и кредита до погашения
        account_from_db = Account.get_account_by_id(db_session, account_id)
        credit_from_db = Credit.get_credit_by_id(db_session, credit_id)

        assert account_from_db is not None, 'Счёт не найден в БД'
        assert credit_from_db is not None, 'Кредит не найден в БД'

        assert credit_from_db.account_id == account_id, 'Кредит связан с неверным счётом'
        assert account_from_db.balance == create_credit_response.balance, 'В БД неверный баланс счёта перед погашением'
        assert credit_from_db.balance == -repay_amount, 'Баланс кредита не соответствует сумме полного погашения'

        # Сохраняем исходные балансы числами
        account_balance_before = account_from_db.balance
        credit_balance_before = credit_from_db.balance

        credit_repay_request = CreditRepayRequest(
            creditId=create_credit_response.creditId,
            accountId=create_credit_response.id,
            amount=repay_amount
        )

        credit_repay_response = api_manager.user_steps.repay_credit(create_credit_secret_request, credit_repay_request)

        assert credit_repay_response.creditId == create_credit_response.creditId
        assert credit_repay_response.amountDeposited == repay_amount

        # Повторно получаем состояние после погашения
        account_from_db = Account.get_account_by_id(db_session, account_id)
        credit_from_db = Credit.get_credit_by_id(db_session, credit_id)

        assert account_from_db is not None, 'После погашения счёт не найден в БД'
        assert credit_from_db is not None, 'После погашения кредит не найден в БД'

        assert account_from_db.balance == account_balance_before - repay_amount, 'В БД неверный баланс счёта после погашения'
        assert credit_from_db.balance == credit_balance_before + repay_amount, 'В БД неверный баланс кредита после погашения'

        # Проверяем операции по счёту
        transactions_from_db = Transaction.get_transactions_by_account_id(db_session, account_id)

        assert len(transactions_from_db) == 2, 'После выдачи и погашения кредита должны быть сохранены две операции'

        # Проверяем наличие операции выдачи
        assert transactions_from_db[0].transaction_type == "credit_issuance"
        assert transactions_from_db[0].amount == create_credit_response.amount

        # Проверяем операцию погашения
        repay_transaction = transactions_from_db[1]

        assert repay_transaction.transaction_type == "credit_repayment", 'В БД сохранён неверный тип операции погашения'
        assert repay_transaction.from_account_id == account_id, 'В операции погашения указан неверный счёт списания'
        assert repay_transaction.to_account_id is None, 'В операции погашения неожиданно указан счёт получателя'
        assert repay_transaction.credit_id == credit_id, 'Операция погашения связана с неверным кредитом'
        assert repay_transaction.amount == repay_amount, 'В БД сохранена неверная сумма погашения'
        assert repay_transaction.created_at is not None, 'В БД отсутствует дата создания операции погашения'

    # Негативные проверки:
    def test_repay_credit_invalid(self, db_session: Session, api_manager: ApiManager,
                                  create_credit_secret_request: CreateCreditSecretRequest, create_credit_response):
        repay_amount = 2500

        account_id = create_credit_response.id
        credit_id = create_credit_response.creditId

        # Проверяем подготовленные счёт и кредит
        account_from_db = Account.get_account_by_id(db_session, account_id)
        credit_from_db = Credit.get_credit_by_id(db_session, credit_id)

        assert account_from_db is not None, 'Счёт не найден в БД'
        assert credit_from_db is not None, 'Кредит не найден в БД'

        assert credit_from_db.account_id == account_id
        assert account_from_db.balance == create_credit_response.balance
        assert credit_from_db.balance == -create_credit_response.amount

        # Сохраняем балансы до запроса
        account_balance_before = account_from_db.balance
        credit_balance_before = credit_from_db.balance

        # Запоминаем существующую операцию выдачи
        transactions_before = Transaction.get_transactions_by_account_id(db_session, account_id)

        assert len(transactions_before) == 1, 'До погашения должна существовать одна операция выдачи кредита'
        assert transactions_before[0].transaction_type == "credit_issuance"

        transaction_ids_before = [transaction.id for transaction in transactions_before]

        credit_repay_request = CreditRepayRequest(
            creditId=create_credit_response.creditId,
            accountId=create_credit_response.id,
            amount=repay_amount
        )

        api_manager.user_steps.repay_invalid_credit(create_credit_secret_request, credit_repay_request)

        # Проверяем балансы после отказа
        account_from_db = Account.get_account_by_id(db_session, account_id)
        credit_from_db = Credit.get_credit_by_id(db_session, credit_id)

        assert account_from_db is not None, 'После отказа счёт исчез из БД'
        assert credit_from_db is not None, 'После отказа кредит исчез из БД'

        assert account_from_db.balance == account_balance_before, 'После отклонённого погашения изменился баланс счёта'
        assert credit_from_db.balance == credit_balance_before, 'После отклонённого погашения изменился баланс кредита'
        assert credit_from_db.account_id == account_id, 'После отказа кредит оказался связан с другим счётом'

        # Проверяем, что набор операций остался прежним
        transactions_after = Transaction.get_transactions_by_account_id(db_session, account_id)

        transaction_ids_after = [transaction.id for transaction in transactions_after]

        assert transaction_ids_after == transaction_ids_before, 'После отклонённого погашения изменился список операций в БД'