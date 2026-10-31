from uuid import uuid4
import requests
import pytest


@pytest.mark.api_jun
class TestRepayCredit:
    # Позитивные проверки:
    def test_repay_credit_valid(self):
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

        create_account_response = requests.post(
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
        assert request_credit_response.json().get("id") == account_id
        assert request_credit_response.json().get("amount") == amount
        assert request_credit_response.json().get("termMonths") == term_months
        assert request_credit_response.json().get("balance") == start_balance + amount
        credit_id = request_credit_response.json().get("creditId")
        assert credit_id is not None
        new_balance = request_credit_response.json().get("balance")

        # Погашаем кредит единовременно на всю сумму
        repay_credit_response = requests.post(
            url="http://localhost:4111/api/credit/repay",
            json={
                "creditId": credit_id,
                "accountId": account_id,
                "amount": amount
            },
            headers={
                "Authorization": f"Bearer {user_token}",
                "accept": "application/json"
            }
        )

        assert repay_credit_response.status_code == 200
        assert repay_credit_response.json().get("creditId") == credit_id
        assert repay_credit_response.json().get("amountDeposited") == amount

        # Проверяем, что со счёта списалась сумма погашения кредита
        account_transactions_response = requests.get(
            url=f"http://localhost:4111/api/account/transactions/{account_id}",
            headers={
                "Authorization": f"Bearer {user_token}",
                "accept": "application/json"
            }
        )

        assert account_transactions_response.status_code == 200
        assert account_transactions_response.json().get("id") == account_id
        assert account_transactions_response.json().get("balance") == new_balance - amount

        # Проверяем, что кредит погашен, т.е. баланс кредита равен 0, а не минус
        credit_history_response = requests.get(
            url="http://localhost:4111/api/credit/history",
            headers={
                "Authorization": f"Bearer {user_token}",
                "accept": "application/json"
            }
        )

        assert credit_history_response.status_code == 200

        credit_balance = None
        for credit in credit_history_response.json().get("credits"):
            if credit.get("creditId") == credit_id:
                credit_balance = credit.get("balance")
                break

        assert credit_balance == 0

    # Негативные проверки:
    def test_repay_credit_invalid(self):
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

        create_account_response = requests.post(
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
        assert request_credit_response.json().get("id") == account_id
        assert request_credit_response.json().get("amount") == amount
        assert request_credit_response.json().get("termMonths") == term_months
        assert request_credit_response.json().get("balance") == start_balance + amount
        credit_id = request_credit_response.json().get("creditId")
        assert credit_id is not None
        new_balance = request_credit_response.json().get("balance")

        # Пытаемся погасить кредит частично
        repay_amount = 2500
        repay_credit_response = requests.post(
            url="http://localhost:4111/api/credit/repay",
            json={
                "creditId": credit_id,
                "accountId": account_id,
                "amount": repay_amount
            },
            headers={
                "Authorization": f"Bearer {user_token}",
                "accept": "application/json"
            }
        )

        assert repay_credit_response.status_code == 422

        # Проверяем, что со счёта действительно ничего не списалось
        account_transactions_response = requests.get(
            url=f"http://localhost:4111/api/account/transactions/{account_id}",
            headers={
                "Authorization": f"Bearer {user_token}",
                "accept": "application/json"
            }
        )

        assert account_transactions_response.status_code == 200
        assert account_transactions_response.json().get("id") == account_id
        assert account_transactions_response.json().get("balance") == new_balance

