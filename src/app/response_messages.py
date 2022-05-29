from enum import Enum


class ReqMessage(str, Enum):
    SUCCESS_REG = "Successfully registered"
    USER_EXIST = "User already exists"
    ALREADY_LOGIN = "Already logged in"
    NOT_EXIST_USER = "No such user"
    WRONG_PASSWORD = "Wrong password"
    LOGOUT_ACCESS = "Access token has been revoked"
    LOGOUT_REFRESH = "Refresh token has been revoked"
    SUCCESS_LOGIN_CHANGE = "Login changed"
    SUCCESS_PASS_CHANGE="Password changed successful"
    UNEXPECTED_ERROR = "Unexpected error"