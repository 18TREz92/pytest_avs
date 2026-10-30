import requests
import pytest
from uuid import uuid4


@pytest.mark.api_jun
class TestTransferAccount:
    # Позитивные проверки:
    def test_transfer_account_valid(self):
        username = f"Max{uuid4().hex[:8]}"

        login_admin_response = requests.post(
            url="http://localhost:4111/api/auth/token/login",
            json={
                "username": "admin",
                "password": "123456"
            },
            headers={
                "Content-Type": "application/json",
                "accept": "application/json"
            }
        )

        assert login_admin_response.status_code == 200
        admin_token = login_admin_response.json().get("token")

        create_user_response = requests.post(
            url="http://localhost:4111/api/admin/create",
            json={
                "username": username,
                "password": "Pas!sw0rd",
                "role": "ROLE_USER"
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {admin_token}"
            }
        )

        assert create_user_response.status_code == 200

        login_user_response = requests.post(
            url="http://localhost:4111/api/auth/token/login",
            json={
                "username": username,
                "password": "Pas!sw0rd"
            },
            headers={
                "Content-Type": "application/json",
                "accept": "application/json"
            }
        )

        assert login_user_response.status_code == 200
        user_token = login_user_response.json().get("token")

        create_first_account_response = requests.post(  # Создание счёта №1
            url="http://localhost:4111/api/account/create",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {user_token}"
            }
        )
        assert create_first_account_response.status_code == 201
        assert create_first_account_response.json().get("balance") == 0
        first_account_id = create_first_account_response.json().get("id")
        assert first_account_id is not None
        start_balance_first = create_first_account_response.json().get("balance")

        create_second_account_response = requests.post(  # Создание счёта №2
            url="http://localhost:4111/api/account/create",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {user_token}"
            }
        )

        assert create_second_account_response.status_code == 201
        assert create_second_account_response.json().get("balance") == 0
        second_account_id = create_second_account_response.json().get("id")
        assert second_account_id is not None
        assert first_account_id != second_account_id
        start_balance_second = create_second_account_response.json().get("balance")

        # Пополняем счёт № 1
        amount = 2000
        deposit_first_account_response = requests.post(
            url="http://localhost:4111/api/account/deposit",
            json={
                "accountId": first_account_id,
                "amount": amount
            },
            headers={
                "Authorization": f"Bearer {user_token}",
                "accept": "application/json"
            }
        )

        assert deposit_first_account_response.status_code == 200
        assert deposit_first_account_response.json().get("balance") == start_balance_first + amount
        new_balance_first = deposit_first_account_response.json().get("balance")

        # Переводим на счёт №2 минимальную сумму
        min_transfer = 500
        transfer_from_first_account_response = requests.post(
            url="http://localhost:4111/api/account/transfer",
            json={
                "fromAccountId": first_account_id,
                "toAccountId": second_account_id,
                "amount": min_transfer
            },
            headers={
                "Authorization": f"Bearer {user_token}",
                "accept": "application/json"
            }
        )

        assert transfer_from_first_account_response.status_code == 200
        assert transfer_from_first_account_response.json().get(
            "fromAccountIdBalance") == new_balance_first - min_transfer

        # Проверим, что баланс счёта №2 успешно пополнился
        second_account_transactions_response = requests.get(
            url=f"http://localhost:4111/api/account/transactions/{second_account_id}",
            headers={
                "Authorization": f"Bearer {user_token}",
                "accept": "application/json"
            }
        )
        assert second_account_transactions_response.status_code == 200
        assert second_account_transactions_response.json().get("balance") == start_balance_second + min_transfer

    # Негативные проверки
    @pytest.mark.parametrize(
        "transfer",
        [499.99, 10000.01]
    )
    def test_transfer_account_invalid(self, transfer):
        username = f"Max{uuid4().hex[:8]}"

        login_admin_response = requests.post(
            url="http://localhost:4111/api/auth/token/login",
            json={
                "username": "admin",
                "password": "123456"
            },
            headers={
                "Content-Type": "application/json",
                "accept": "application/json"
            }
        )

        assert login_admin_response.status_code == 200
        admin_token = login_admin_response.json().get("token")

        create_user_response = requests.post(
            url="http://localhost:4111/api/admin/create",
            json={
                "username": username,
                "password": "Pas!sw0rd",
                "role": "ROLE_USER"
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {admin_token}"
            }
        )

        assert create_user_response.status_code == 200

        login_user_response = requests.post(
            url="http://localhost:4111/api/auth/token/login",
            json={
                "username": username,
                "password": "Pas!sw0rd"
            },
            headers={
                "Content-Type": "application/json",
                "accept": "application/json"
            }
        )

        assert login_user_response.status_code == 200
        user_token = login_user_response.json().get("token")

        create_first_account_response = requests.post(  # Создание счёта №1
            url="http://localhost:4111/api/account/create",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {user_token}"
            }
        )
        assert create_first_account_response.status_code == 201
        assert create_first_account_response.json().get("balance") == 0
        first_account_id = create_first_account_response.json().get("id")
        assert first_account_id is not None
        start_balance_first = create_first_account_response.json().get("balance")

        create_second_account_response = requests.post(  # Создание счёта №2
            url="http://localhost:4111/api/account/create",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {user_token}"
            }
        )

        assert create_second_account_response.status_code == 201
        assert create_second_account_response.json().get("balance") == 0
        second_account_id = create_second_account_response.json().get("id")
        assert second_account_id is not None
        assert first_account_id != second_account_id
        start_balance_second = create_second_account_response.json().get("balance")

        # Пополняем счёт № 1 на максимально возможную сумму
        amount_max = 9000
        deposit_first_account_response = requests.post(
            url="http://localhost:4111/api/account/deposit",
            json={
                "accountId": first_account_id,
                "amount": amount_max
            },
            headers={
                "Authorization": f"Bearer {user_token}",
                "accept": "application/json"
            }
        )

        assert deposit_first_account_response.status_code == 200
        assert deposit_first_account_response.json().get("balance") == start_balance_first + amount_max
        new_balance_first = deposit_first_account_response.json().get("balance")

        # Пополняем счёт №1 ещё раз, чтобы потом можно было проверить верхнюю границу перевода
        amount = 2000
        deposit_first_account_response = requests.post(
            url="http://localhost:4111/api/account/deposit",
            json={
                "accountId": first_account_id,
                "amount": amount
            },
            headers={
                "Authorization": f"Bearer {user_token}",
                "accept": "application/json"
            }
        )

        assert deposit_first_account_response.status_code == 200
        assert deposit_first_account_response.json().get("balance") == new_balance_first + amount
        newest_balance_first = deposit_first_account_response.json().get("balance")

        # Переводим на счёт №2 сумму меньше/больше минимальной/максимальной
        transfer_from_first_account_response = requests.post(
            url="http://localhost:4111/api/account/transfer",
            json={
                "fromAccountId": first_account_id,
                "toAccountId": second_account_id,
                "amount": transfer
            },
            headers={
                "Authorization": f"Bearer {user_token}",
                "accept": "application/json"
            }
        )

        assert transfer_from_first_account_response.status_code == 400

        # Проверим, что баланс счёта №1 не изменился
        first_account_transactions_response = requests.get(
            url=f"http://localhost:4111/api/account/transactions/{first_account_id}",
            headers={
                "Authorization": f"Bearer {user_token}",
                "accept": "application/json"
            }
        )
        assert first_account_transactions_response.status_code == 200
        assert first_account_transactions_response.json().get("balance") == newest_balance_first

        # Проверим, что баланс счёта №2 не изменился
        second_account_transactions_response = requests.get(
            url=f"http://localhost:4111/api/account/transactions/{second_account_id}",
            headers={
                "Authorization": f"Bearer {user_token}",
                "accept": "application/json"
            }
        )
        assert second_account_transactions_response.status_code == 200
        assert second_account_transactions_response.json().get("balance") == start_balance_second
