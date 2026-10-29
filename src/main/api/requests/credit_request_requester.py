from http import HTTPStatus
import requests
from src.main.api.models.credit_request_request import CreditRequestRequest
from src.main.api.models.credit_request_response import CreditRequestResponse
from src.main.api.requests.requester import Requester


class CreditRequestRequester(Requester):
    def post(self, credit_request_request: CreditRequestRequest) -> CreditRequestResponse | Response:
        url = f"{self.base_url}/credit/request"
        response = requests.post(
            url=url,
            json=credit_request_request.model_dump(),
            headers=self.headers
        )
        self.response_spec(response)
        if response.status_code in [HTTPStatus.OK, HTTPStatus.CREATED]:
            return CreditRequestResponse(**response.json())
        return response