from uuid import uuid4
import requests
import pytest


@pytest.mark.api_jun
class TestRequestCredit:
    # Позитивные проверки:
    def test_request_credit_valid(self):
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
                "role": "ROLE_CREDIT_SECRET"
            },
            headers={
                "Authorization": f"Bearer {admin_token}",
                "accept": "application/json"
            }
        )

        assert create_user_response.status_code == 200
        assert create_user_response.json()["role"] == "ROLE_CREDIT_SECRET"

        login_user_response = requests.post(
            url="http://localhost:4111/api/auth/token/login",
            json={
                "username": username,
                "password": "Pas!sw0rd"
            },
            headers={
                "accept": "application/json"
            }
        )

        assert login_user_response.status_code == 200
        user_token = login_user_response.json().get("token")

        create_account_response = requests.post(  # Создание счёта
            url="http://localhost:4111/api/account/create",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {user_token}"
            }
        )
        assert create_account_response.status_code == 201
        assert create_account_response.json().get("balance") == 0
        account_id = create_account_response.json().get("id")
        assert account_id is not None
        start_balance = create_account_response.json().get("balance")

        # Берём кредит на минимальную сумму
        amount = 5000
        term_months = 12

        request_credit_response = requests.post(
            url="http://localhost:4111/api/credit/request",
            json={
                "accountId": account_id,
                "amount": amount,
                "termMonths": term_months
            },
            headers={
                "Authorization": f"Bearer {user_token}",
                "accept": "application/json"
            }
        )

        assert request_credit_response.status_code == 201
        # В фактическом ответе из Swagger идентификатор счёта называется "id".
        assert request_credit_response.json().get("id") == account_id
        assert request_credit_response.json().get("amount") == amount
        assert request_credit_response.json().get("termMonths") == term_months
        assert request_credit_response.json().get("balance") == start_balance + amount
        assert request_credit_response.json().get("creditId") is not None

        # Проверяем, что деньги действительно зачислены на счёт.
        first_account_transactions_response = requests.get(
            url=f"http://localhost:4111/api/account/transactions/{account_id}",
            headers={
                "Authorization": f"Bearer {user_token}",
                "accept": "application/json"
            }
        )

        assert first_account_transactions_response.status_code == 200
        assert first_account_transactions_response.json().get("id") == account_id
        assert first_account_transactions_response.json().get("balance") == start_balance + amount

    # Негативные проверки: сумма ниже минимума и выше максимума.

    @pytest.mark.parametrize(
        "amount",
        [4999.99, 15000.01]
    )
    def test_request_credit_invalid(self, amount):
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
                "role": "ROLE_CREDIT_SECRET"
            },
            headers={
                "Authorization": f"Bearer {admin_token}",
                "accept": "application/json"
            }
        )

        assert create_user_response.status_code == 200
        assert create_user_response.json()["role"] == "ROLE_CREDIT_SECRET"

        login_user_response = requests.post(
            url="http://localhost:4111/api/auth/token/login",
            json={
                "username": username,
                "password": "Pas!sw0rd"
            },
            headers={
                "accept": "application/json"
            }
        )

        assert login_user_response.status_code == 200
        user_token = login_user_response.json().get("token")

        create_account_response = requests.post(  # Создание счёта
            url="http://localhost:4111/api/account/create",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {user_token}"
            }
        )
        assert create_account_response.status_code == 201
        assert create_account_response.json().get("balance") == 0
        account_id = create_account_response.json().get("id")
        assert account_id is not None
        start_balance = create_account_response.json().get("balance")

        term_months = 12
        request_credit_response = requests.post(
            url="http://localhost:4111/api/credit/request",
            json={
                "accountId": account_id,
                "amount": amount,
                "termMonths": term_months
            },
            headers={
                "Authorization": f"Bearer {user_token}",
                "accept": "application/json"
            }
        )

        assert request_credit_response.status_code == 400

        # После отказа баланс счёта должен остаться прежним.
        account_transactions_response = requests.get(
            url=f"http://localhost:4111/api/account/transactions/{account_id}",
            headers={
                "Authorization": f"Bearer {user_token}",
                "accept": "application/json"
            }
        )

        assert account_transactions_response.status_code == 200
        assert account_transactions_response.json().get("id") == account_id
        assert account_transactions_response.json().get("balance") == start_balance
