import pytest
from sqlalchemy.orm import Session
from src.main.api.classes.api_manager import ApiManager
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.db.crud.user_crud import UserCrudDb as User


@pytest.mark.api_sen
class TestCreateAccount:
    # Позитивные проверки:
    def test_create_account_valid(self, db_session: Session, api_manager: ApiManager,
                                  create_user_request: CreateUserRequest):
        # Создание счёта №1
        first_response = api_manager.user_steps.create_account(create_user_request)

        assert first_response.balance == 0
        assert first_response.id is not None
        first_account_id = first_response.id

        first_account_from_db = Account.get_account_by_id(db_session, first_account_id)
        assert first_account_from_db.id == first_account_id, 'Первый аккаунт не создан, id аккаунта нет в БД'
        assert first_account_from_db.balance is not None, 'Поле баланса для созданного аккаунта отсутствует в БД'

        # Создание счёта №2
        second_response = api_manager.user_steps.create_account(create_user_request)

        assert second_response.balance == 0
        assert second_response.id is not None
        second_account_id = second_response.id
        assert first_account_id != second_account_id

        second_account_from_db = Account.get_account_by_id(db_session, second_account_id)
        assert second_account_from_db.id == second_account_id, 'Второй аккаунт не создан, id аккаунта нет в БД'
        assert second_account_from_db.balance is not None, 'Поле баланса для созданного аккаунта отсутствует в БД'

    # Негативные проверки:
    def test_create_account_invalid_by_admin(self, db_session: Session,
                                             api_manager: ApiManager):  # Создание счёта в роли админа
        # Получаем администратора из БД
        admin_from_db = User.get_user_by_username(db_session, "admin")
        assert admin_from_db is not None, "Администратор не найден в БД"

        # Получаем идентификаторы его счетов до запроса
        accounts_before = Account.get_accounts_by_user_id(db_session, admin_from_db.id)
        account_ids_before = [account.id for account in accounts_before]

        # Пытаемся создать счёт в роли администратора
        api_manager.admin_steps.admin_create_account()

        # Получаем идентификаторы его счетов после запроса
        accounts_after = Account.get_accounts_by_user_id(db_session, admin_from_db.id)
        account_ids_after = [account.id for account in accounts_after]

        assert account_ids_after == account_ids_before, 'После запрещённого создания счёта изменился список счетов администратора в БД'

    def test_create_third_account_invalid(self, db_session: Session, api_manager: ApiManager,
                                          create_user_request: CreateUserRequest):  # Создание третьего счёта
        # Создание счёта №1
        first_response = api_manager.user_steps.create_account(create_user_request)

        assert first_response.balance == 0
        assert first_response.id is not None
        first_account_id = first_response.id

        # Создание счёта №2
        second_response = api_manager.user_steps.create_account(create_user_request)

        assert second_response.balance == 0
        assert second_response.id is not None
        second_account_id = second_response.id
        assert first_account_id != second_account_id

        # Получаем пользователя из БД
        user_from_db = User.get_user_by_username(db_session, create_user_request.username)
        assert user_from_db is not None, "Пользователь не найден в БД"

        # Проверяем, что в БД сохранены ровно два созданных счёта
        accounts_before = Account.get_accounts_by_user_id(db_session, user_from_db.id)
        account_ids_before = [account.id for account in accounts_before]

        assert account_ids_before == sorted(
            [first_account_id, second_account_id]), 'В БД должны быть ровно два созданных счёта пользователя'

        # Создание счёта №3
        api_manager.user_steps.create_invalid_account(create_user_request)

        # Проверяем, что после отказа список счетов не изменился
        accounts_after = Account.get_accounts_by_user_id(db_session, user_from_db.id)
        account_ids_after = [account.id for account in accounts_after]

        assert account_ids_after == account_ids_before, 'После отказа в создании третьего счёта изменился список счетов пользователя в БД'
