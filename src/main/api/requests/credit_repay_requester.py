from http import HTTPStatus
import requests
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.models.credit_repay_response import CreditRepayResponse
from src.main.api.requests.requester import Requester


class CreditRepayRequester(Requester):
    def post(self, credit_repay_request: CreditRepayRequest) -> CreditRepayResponse | Response:
        url = f"{self.base_url}/credit/repay"
        response = requests.post(
            url=url,
            json=credit_repay_request.model_dump(),
            headers=self.headers
        )
        self.response_spec(response)
        if response.status_code in [HTTPStatus.OK, HTTPStatus.CREATED]:
            return CreditRepayResponse(**response.json())
        return response