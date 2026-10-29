from requests import Response
from http import HTTPStatus


class ResponseSpecs:
    @staticmethod
    def request_ok():                                                             # 200
        def confirm(response: Response):
            assert response.status_code == HTTPStatus.OK, response.text
        return confirm

    @staticmethod
    def request_created():                                                        # 201
        def confirm(response: Response):
            assert response.status_code == HTTPStatus.CREATED, response.text
        return confirm

    @staticmethod
    def request_bad():                                                            # 400
        def confirm(response: Response):
            assert response.status_code == HTTPStatus.BAD_REQUEST, response.text
        return confirm

    @staticmethod
    def request_unauthorized():                                                   # 401
        def confirm(response: Response):
            assert response.status_code == HTTPStatus.UNAUTHORIZED, response.text
        return confirm

    @staticmethod
    def request_forbidden():                                                      # 403
        def confirm(response: Response):
            assert response.status_code == HTTPStatus.FORBIDDEN, response.text
        return confirm

    @staticmethod
    def request_conflict():                                                       # 409
        def confirm(response: Response):
            assert response.status_code == HTTPStatus.CONFLICT, response.text
        return confirm

    @staticmethod
    def request_bad_content():                                                    # 422
        def confirm(response: Response):
            assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT, response.text
        return confirm