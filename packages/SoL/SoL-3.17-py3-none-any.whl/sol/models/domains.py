# -*- coding: utf-8 -*-
#:Progetto:  SoL -- Data domains
#:Creato:    mar 09 apr 2013 10:31:33 CEST
#:Autore:    Lele Gaifax <lele@metapensiero.it>
#:Licenza:   GNU General Public License version 3 or later
#

from decimal import Decimal
from sqlalchemy import (
    Boolean,
    CHAR,
    Date,
    DateTime,
    Integer,
    SmallInteger,
    Unicode,
    VARCHAR,
    )
from sqlalchemy.types import TypeDecorator


class Description(TypeDecorator):
    impl = Unicode

    def process_bind_param(self, value, dialect):
        from .utils import asunicode, normalize

        return normalize(asunicode(value))


class Name(TypeDecorator):
    impl = Unicode

    def process_bind_param(self, value, dialect):
        from .utils import asunicode, normalize

        return normalize(asunicode(value), True)


class PreciseDecimalNumber(TypeDecorator):
    """A decimal number with a fixed precision stored as an integer"""

    impl = Integer
    precisionfactor = 10 ** 0

    def process_bind_param(self, value, dialect):
        if value is None:
            return None

        if not isinstance(value, Decimal):
            value = Decimal(value)

        return int(value * self.precisionfactor)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        else:
            return Decimal(value) / self.precisionfactor


class Prize(PreciseDecimalNumber):
    precisionfactor = 10 ** 2


class Volatility(PreciseDecimalNumber):
    precisionfactor = 10 ** 5


boolean_t = Boolean()
"A boolean value, either True or False"

code_t = VARCHAR(10)
"A string code"

date_t = Date()
"A date"

timestamp_t = DateTime()
"A date stamp"

description_t = Description(50)
"A fifty characters long description"

email_t = VARCHAR(50)
"An email address"

filename_t = Unicode(40)
"A file name"

flag_t = CHAR(1)
"A single character used as some sort of flag"

guid_t = CHAR(32)
"A globally unique id"

int_t = Integer()
"An integer value"

intid_t = Integer()
"An integer value, commonly used as the primary key"

language_t = CHAR(2)
"A ISO 639-1 language code"

name_t = Name(50)
"A fifty characters long name"

nationality_t = CHAR(3)
"A ISO 3166 country code"

nickname_t = Unicode(15)
"A short string used for nicknames"

password_t = VARCHAR(60)
"A password hash"

phone_t = VARCHAR(20)
"A phone number"

prize_t = Prize()
"A number with two decimal digits, but stored as an integer"

smallint_t = SmallInteger()
"A small integer number"

url_t = VARCHAR(50)
"A web URL"

volatility_t = Volatility()
"A number with five decimal digits, but stored as an integer"
