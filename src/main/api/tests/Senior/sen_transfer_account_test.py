import pytest
from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.transfer_account_request import TransferAccountRequest
from sqlalchemy.orm import Session
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.utils import calculate_balance_after_transfer


@pytest.mark.api_sen
class TestTransferAccount:
    # Позитивные проверки:
    def test_transfer_account_valid(self, db_session: Session, api_manager: ApiManager,
                                    create_user_request: CreateUserRequest, prepare_accounts_for_transfer):
        from_account, to_account, from_balance = prepare_accounts_for_transfer
        transfer_amount = RandomModelGenerator.generate_transfer_amount(from_balance)

        transfer_response = api_manager.user_steps.transfer_account(
            create_user_request,
            TransferAccountRequest(
                fromAccountId=from_account.id,
                toAccountId=to_account.id,
                amount=transfer_amount
            )
        )

        expected_balance = calculate_balance_after_transfer(from_balance, transfer_amount)

        assert transfer_response.fromAccountIdBalance == expected_balance, 'Баланс отправителя в ответе API не уменьшился на сумму перевода'

        account_from_db = Account.get_account_by_id(db_session, from_account.id)

        assert (account_from_db is not None and account_from_db.balance == expected_balance), 'Счёт отправителя не найден в БД или с него списана неверная сумма'

    # Негативные проверки
    @pytest.mark.parametrize(
        "transfer_amount",
        [499.99, 10000.01]
    )
    def test_transfer_account_invalid(self, transfer_amount: float, db_session: Session, api_manager: ApiManager,
                                      create_user_request: CreateUserRequest, prepare_accounts_for_transfer):
        from_account, to_account, expected_balance = prepare_accounts_for_transfer

        api_manager.user_steps.transfer_invalid_account(
            create_user_request,
            TransferAccountRequest(
                fromAccountId=from_account.id,
                toAccountId=to_account.id,
                amount=transfer_amount
            )
        )

        account_from_db = Account.get_account_by_id(db_session, from_account.id)

        assert (account_from_db is not None and account_from_db.balance == expected_balance), 'Счёт отправителя не найден в БД или его баланс изменился после отклонённого перевода'
