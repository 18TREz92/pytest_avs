import pytest
from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateCreditSecretRequest
from src.main.api.models.credit_request_request import CreditRequestRequest
from sqlalchemy.orm import Session
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.db.crud.credit_crud import CreditCrudDb as Credit
from src.main.api.db.crud.transaction_crud import TransactionCrudDb as Transaction


@pytest.mark.api_sen
class TestRequestCredit:
    # Позитивные проверки:
    def test_request_credit_valid(self, db_session: Session, api_manager: ApiManager,
                                  create_credit_secret_request: CreateCreditSecretRequest,
                                  create_credit_account_response):
        # Проверяем созданный фикстурой счёт
        assert create_credit_account_response.balance == 0
        assert create_credit_account_response.id is not None

        account_id = create_credit_account_response.id
        start_balance = create_credit_account_response.balance

        # Берём кредит на минимальную сумму
        amount = 5000
        term_months = 12

        credit_request_request = CreditRequestRequest(accountId=account_id, amount=amount, termMonths=term_months)
        credit_response = api_manager.user_steps.request_credit(
            create_credit_secret_request,
            credit_request_request
        )
        # В фактическом ответе из Swagger идентификатор счёта называется "id".
        assert credit_response.id == account_id
        assert credit_response.amount == amount
        assert credit_response.termMonths == term_months
        assert credit_response.balance == start_balance + amount
        assert credit_response.creditId is not None

        # Проверяем зачисление кредитных средств на счёт
        account_from_db = Account.get_account_by_id(db_session, account_id)

        assert account_from_db is not None, 'Счёт не найден в БД'
        assert account_from_db.balance == start_balance + amount, 'В БД неверный баланс счёта после выдачи кредита'

        # Проверяем сохранённый кредит
        credit_from_db = Credit.get_credit_by_id(db_session, credit_response.creditId)

        assert credit_from_db is not None, 'Созданный кредит не найден в БД'
        assert credit_from_db.account_id == account_id, 'Кредит в БД связан с неверным счётом'
        assert credit_from_db.amount == amount, 'В БД сохранена неверная сумма кредита'
        assert credit_from_db.term_months == term_months, 'В БД сохранён неверный срок кредита'
        assert credit_from_db.balance == -amount, 'В БД неверный баланс кредита после выдачи'
        assert credit_from_db.created_at is not None, 'В БД отсутствует дата создания кредита'

        # Проверяем операцию выдачи кредита
        transactions_from_db = Transaction.get_transactions_by_account_id(db_session, account_id)

        assert len(transactions_from_db) == 1, 'После выдачи кредита должна быть сохранена ровно одна операция'

        credit_transaction = transactions_from_db[0]

        assert credit_transaction.to_account_id == account_id, 'В операции выдачи кредита указан неверный счёт получателя'
        assert credit_transaction.from_account_id is None, 'В операции выдачи кредита неожиданно указан счёт отправителя'
        assert credit_transaction.amount == amount, 'В операции сохранена неверная сумма выдачи кредита'
        assert credit_transaction.transaction_type == "credit_issuance", 'В БД сохранён неверный тип операции выдачи кредита'
        assert credit_transaction.created_at is not None, 'В БД отсутствует дата создания операции выдачи кредита'

    # Негативные проверки: сумма ниже минимума и выше максимума.

    @pytest.mark.parametrize(
        "amount",
        [4999.99, 15000.01]
    )
    def test_request_credit_invalid(self, db_session: Session, amount: float, api_manager: ApiManager,
                                    create_credit_secret_request: CreateCreditSecretRequest,
                                    create_credit_account_response):
        # Проверяем созданный фикстурой счёт
        assert create_credit_account_response.balance == 0
        assert create_credit_account_response.id is not None

        account_id = create_credit_account_response.id

        # Проверяем исходный баланс в БД
        account_from_db = Account.get_account_by_id(db_session, account_id)

        assert account_from_db is not None, 'Счёт не найден в БД'
        assert account_from_db.balance == 0

        start_balance = account_from_db.balance

        # У нового счёта ещё нет кредитов
        credits_before = Credit.get_credits_by_account_id(db_session, account_id)
        assert credits_before == [], 'До запроса у нового счёта не должно быть кредитов'

        # У нового счёта ещё нет операций
        transactions_before = Transaction.get_transactions_by_account_id(db_session, account_id)
        assert transactions_before == [], 'До запроса у нового счёта не должно быть операций'

        # Пытаемся оформить кредит на недопустимую сумму
        credit_request_request = CreditRequestRequest(accountId=create_credit_account_response.id, amount=amount,
                                                      termMonths=12)
        api_manager.user_steps.request_invalid_credit(create_credit_secret_request, credit_request_request)

        # Проверяем неизменность баланса
        account_from_db = Account.get_account_by_id(db_session, account_id)

        assert account_from_db is not None, 'После отказа счёт исчез из БД'
        assert account_from_db.balance == start_balance, 'После отклонённой выдачи кредита изменился баланс счёта'

        # Проверяем отсутствие созданного кредита
        credits_after = Credit.get_credits_by_account_id(db_session, account_id)
        assert credits_after == [], 'Несмотря на отказ, в БД создался кредит'

        # Проверяем отсутствие операции
        transactions_after = Transaction.get_transactions_by_account_id(db_session, account_id)
        assert transactions_after == [], 'Несмотря на отказ, в БД сохранилась операция по счёту'