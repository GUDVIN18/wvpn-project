# -*- coding: utf-8 -*-


class ApiError(Exception):
    """
    Неожиданный код ошибки.
    """  # noqa: E501
    __content = None

    HTTP_CODE = 0

    def __init__(self, *args, **kwargs):
        super(ApiError, self).__init__(*args, **kwargs)
        if args[0] is not None:
            self.__content = dict(args[0])

    @property
    def content(self):
        return self.__content
