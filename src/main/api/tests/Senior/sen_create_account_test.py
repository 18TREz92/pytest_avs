import pytest
from sqlalchemy.orm import Session
from src.main.api.classes.api_manager import ApiManager
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.db.crud.user_crud import UserCrudDb as User
from src.main.api.configs.config import Config


@pytest.mark.api_sen
class TestCreateAccount:
    # Позитивные проверки:
    def test_create_account_valid(self, db_session: Session, api_manager: ApiManager,
                                  create_user_request: CreateUserRequest):
        response = api_manager.user_steps.create_account(create_user_request)

        assert response.balance == 0, 'Начальный баланс созданного аккаунта не равен 0'

        account_from_db = Account.get_account_by_id(db_session, response.id)
        assert account_from_db.id == response.id, 'Аккаунт не создан, id аккаунта нет в БД'
        assert account_from_db.balance is not None, 'Поле баланса для созданного аккаунта отсутствует в БД'

    # Негативные проверки:
    def test_create_account_invalid_by_admin(self, db_session: Session,
                                             api_manager: ApiManager):  # Создание счёта в роли админа
        api_manager.admin_steps.admin_create_account()

        admin_from_db = User.get_user_by_username(db_session, Config.fetch("adminUsername"))
        accounts_from_db = Account.get_accounts_by_user_id(db_session, admin_from_db.id)

        assert accounts_from_db == [], 'У администратора обнаружены счета, хотя их создание ему запрещено'