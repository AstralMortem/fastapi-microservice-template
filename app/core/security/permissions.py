from fastapi import Depends
from .dependencies import AccessTokenDep
from .tokens import AccessToken
from app.core.exceptions import ServiceError
from app.conf import settings


class _Credential:
    error: ServiceError

    def __or__(self, other: "_Credential"):
        return _OrCredentialCheck(self, other)

    def __and__(self, other: "_Credential"):
        return _AndCredentialCheck(self, other)

    def validate(self, token: AccessToken) -> bool:
        raise NotImplementedError


class _OrCredentialCheck(_Credential):
    def __init__(self, left: _Credential, right: _Credential):
        self.left = left
        self.right = right

    def validate(self, token: AccessToken) -> bool:
        return self.left.validate(token) or self.right.validate(token)


class _AndCredentialCheck(_Credential):
    def __init__(self, left: _Credential, right: _Credential):
        self.left = left
        self.right = right

    def validate(self, token: AccessToken) -> bool:
        return self.left.validate(token) and self.right.validate(token)


class Role(_Credential):
    def __init__(self, role: str):
        self.role = role.lower()
        self.error = ServiceError(
            403, "Invalid role", f"User does not have the required role"
        )

    def validate(self, token: AccessToken) -> bool:
        if self.role in map(str.lower, token.roles or []):
            return True
        return False


class Permission(_Credential):
    DELIMITER = ":"

    def __init__(self, permission: str, action: str | None = None):
        self.error = ServiceError(
            403, "Invalid permission", f"User does not have the required permission"
        )

        if action is None and permission.count(self.DELIMITER) == 1:
            self.permission, self.action = map(
                str.lower, permission.split(self.DELIMITER)
            )
        elif (
            action is not None
            and action.count(self.DELIMITER) == 0
            and permission.count(self.DELIMITER) == 0
        ):
            self.permission = permission.lower()
            self.action = action.lower()

    def validate(self, token: AccessToken) -> bool:
        permission = f"{self.permission}{self.DELIMITER}{self.action}"
        if permission in map(str.lower, token.permissions or []):
            return True
        return False


def AuthRequired(credential: _Credential):
    if not isinstance(credential, _Credential):
        raise TypeError("Credential must be an instance of _Credential")

    async def _validate(token: AccessTokenDep):
        if not settings.ENABLE_RBAC:
            Warning(
                "RBAC is disabled, skipping permission checks. If you want to use token, call use AccessTokenDep directly"
            )
            return token
        if credential.validate(token):
            return token
        raise credential.error

    return Depends(_validate)
