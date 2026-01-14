# -*- coding: utf-8 -*-
from yookassa.domain.exceptions.api_error import ApiError


class InternalServerError(ApiError):
    """
    Ошибка авторизации. Не установлен заголовок.
    """  # noqa: E501
    HTTP_CODE = 500
