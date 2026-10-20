from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse


class AppException(HTTPException):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=message)
        self.code = code
        self.message = message
        self.details = details or {}


class NotFoundException(AppException):
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="RESOURCE_NOT_FOUND",
            message=f"{resource} with identifier '{identifier}' was not found.",
            details={"resource": resource, "identifier": str(identifier)},
        )


class ConflictException(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code="RESOURCE_CONFLICT",
            message=message,
            details=details,
        )


class ValidationException(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="VALIDATION_ERROR",
            message=message,
            details=details,
        )


class InsufficientStockException(AppException):
    def __init__(self, medicine_id: str, current_stock: int, requested_qty: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INSUFFICIENT_STOCK",
            message=f"Stock for medicine '{medicine_id}' cannot drop below zero. Current stock is {current_stock}, requested reduction is {requested_qty}.",
            details={
                "medicine_id": medicine_id,
                "current_stock": current_stock,
                "requested_quantity": requested_qty,
            },
        )


class ForbiddenException(AppException):
    def __init__(self, message: str = "You do not have sufficient permissions to perform this action."):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="PERMISSION_DENIED",
            message=message,
        )


def format_error_response(code: str, message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        }
    }
