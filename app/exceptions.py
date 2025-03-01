from fastapi import HTTPException
from starlette import status

class BillingError(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class ClientNotFoundError(BillingError):
    def __init__(self, detail: str = "Client not found"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)