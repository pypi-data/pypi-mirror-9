# -*- coding: utf-8 -*-

from sqlalchemy import (
    Boolean,
    DateTime,
    SmallInteger,
    Unicode,
    VARCHAR,
    )


boolean_t = Boolean()
"A boolean value, either True or False"

name_t = VARCHAR(63)
"A symbol name, as stored in the database"

password_t = VARCHAR(60)
"A password"

shortstring_t = Unicode(50)
"A short string"

smallint_t = SmallInteger()
"A small integer number"

timestamp_t = DateTime()
"A precise point in time"
