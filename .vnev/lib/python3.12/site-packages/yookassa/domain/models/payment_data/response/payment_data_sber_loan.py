# -*- coding: utf-8 -*-
import re

from yookassa.domain.common.payment_method_type import PaymentMethodType
from yookassa.domain.models import Amount
from yookassa.domain.models.payment_data.payment_data import ResponsePaymentData


class PaymentDataSberLoan(ResponsePaymentData):
    """
    Оплата в кредит или рассрочку от СберБанка.
    """  # noqa: E501

    __loan_option = None
    """Тариф кредита, который пользователь выбрал при оплате. 
    Возможные значения:  
    `loan` — кредит; 
    `installments_XX` — рассрочка, где ~`XX` — количество месяцев для выплаты рассрочки. Например, ~`installments_3` — рассрочка на 3 месяца.  Присутствует для платежей в статусе ~`waiting_for_capture` и ~`succeeded`. """  # noqa: E501

    __discount_amount = None
    """Сумма скидки для рассрочки."""  # noqa: E501

    def __init__(self, *args, **kwargs):
        super(PaymentDataSberLoan, self).__init__(*args, **kwargs)
        if self.type is None or self.type is not PaymentMethodType.SBER_LOAN:
            self.type = PaymentMethodType.SBER_LOAN

    @property
    def loan_option(self):
        """
        Возвращает loan_option модели PaymentDataSberLoan.

        :return: loan_option модели PaymentDataSberLoan.
        :rtype: str
        """
        return self.__loan_option

    @loan_option.setter
    def loan_option(self, value):
        """
        Устанавливает loan_option модели PaymentDataSberLoan.

        :param value: loan_option модели PaymentDataSberLoan.
        :type value: str
        """
        cast_value = str(value)
        if re.match('^loan|installments_([0-9]+)$', cast_value):
            self.__loan_option = cast_value
        else:
            raise ValueError('Invalid loan_option value type')

    @property
    def discount_amount(self):
        """
        Возвращает discount_amount модели PaymentDataSberLoan.

        :return: discount_amount модели PaymentDataSberLoan.
        :rtype: Amount
        """
        return self.__discount_amount

    @discount_amount.setter
    def discount_amount(self, value):
        """
        Устанавливает discount_amount модели PaymentDataSberLoan.

        :param value: discount_amount модели PaymentDataSberLoan.
        :type value: Amount
        """
        if isinstance(value, dict):
            self.__discount_amount = Amount(value)
        elif isinstance(value, Amount):
            self.__discount_amount = value
        else:
            raise TypeError('Invalid discount_amount value type')
