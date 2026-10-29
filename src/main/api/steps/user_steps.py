from src.main.api.foundation.endpoint import Endpoint
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.foundation.requesters.validate_crud_requester import ValidateCrudRequester
from src.main.api.models.create_user_request import CreateUserRequest, CreateCreditSecretRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.models.credit_request_request import CreditRequestRequest
from src.main.api.models.deposit_account_request import DepositAccountRequest
from src.main.api.models.transfer_account_request import TransferAccountRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.steps.base_steps import BaseSteps


class UserSteps(BaseSteps):
    def create_account(self, create_user_request: CreateUserRequest | CreateCreditSecretRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.CREATE_ACCOUNT,
            ResponseSpecs.request_created()
        ).post()
        return response

    def create_invalid_account(self, create_user_request: CreateUserRequest):
        CrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.CREATE_ACCOUNT,
            ResponseSpecs.request_conflict()
        ).post(None)

    def deposit_account(self, create_user_request: CreateUserRequest, deposit_account_request: DepositAccountRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.DEPOSIT_ACCOUNT,
            ResponseSpecs.request_ok()
        ).post(deposit_account_request)
        return response

    def deposit_invalid_account(self, create_user_request: CreateUserRequest, deposit_account_request: DepositAccountRequest):
        CrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.DEPOSIT_ACCOUNT,
            ResponseSpecs.request_bad()
        ).post(deposit_account_request)

    def transfer_account(self, create_user_request: CreateUserRequest, transfer_account_request: TransferAccountRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.TRANSFER_ACCOUNT,
            ResponseSpecs.request_ok()
        ).post(transfer_account_request)
        return response

    def transfer_invalid_account(self, create_user_request: CreateUserRequest, transfer_account_request: TransferAccountRequest):
        CrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.TRANSFER_ACCOUNT,
            ResponseSpecs.request_bad()
        ).post(transfer_account_request)

    def request_credit(self, create_credit_secret_request: CreateCreditSecretRequest, credit_request_request: CreditRequestRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_credit_secret_request.username, password=create_credit_secret_request.password),
            Endpoint.CREDIT_REQUEST,
            ResponseSpecs.request_created()
        ).post(credit_request_request)
        return response

    def request_invalid_credit(self, create_credit_secret_request: CreateCreditSecretRequest, credit_request_request: CreditRequestRequest):
        CrudRequester(
            RequestSpecs.auth_headers(username=create_credit_secret_request.username, password=create_credit_secret_request.password),
            Endpoint.CREDIT_REQUEST,
            ResponseSpecs.request_bad()
        ).post(credit_request_request)

    def repay_credit(self, create_credit_secret_request: CreateCreditSecretRequest, credit_repay_request: CreditRepayRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_credit_secret_request.username, password=create_credit_secret_request.password),
            Endpoint.CREDIT_REPAY,
            ResponseSpecs.request_ok()
        ).post(credit_repay_request)
        return response

    def repay_invalid_credit(self, create_credit_secret_request: CreateCreditSecretRequest, credit_repay_request: CreditRepayRequest):
        CrudRequester(
            RequestSpecs.auth_headers(username=create_credit_secret_request.username, password=create_credit_secret_request.password),
            Endpoint.CREDIT_REPAY,
            ResponseSpecs.request_bad_content()
        ).post(credit_repay_request)