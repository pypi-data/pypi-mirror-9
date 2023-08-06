"""
SQLAlchemy-backed user/group implementation.
"""

import logging

from sqlalchemy import Column, func
from sqlalchemy.ext.hybrid import hybrid_property

from cryptacular.bcrypt import BCRYPTPasswordManager

from ..i18n import translatable_string as _
from . import Base
from .domains import (
    boolean_t,
    name_t,
    password_t,
    shortstring_t,
    smallint_t,
    timestamp_t,
    )

logger = logging.getLogger(__name__)


class User(Base):
    """An authenticated user of the system.
    """

    __tablename__ = 'users'

    crypt = BCRYPTPasswordManager()
    "The crypt engine used for the password field"

    user_id = Column(
        smallint_t,
        primary_key=True,
        nullable=False,
        info=dict(
            label=_('User ID'),
            hint=_('Unique ID of this user'),
            )
        )
    "The ID of the user"

    username = Column(
        name_t,
        unique=True,
        nullable=False,
        info=dict(
            label=_('User name'),
            hint=_('Unique name of this user, for authentication purpose'),
            )
        )
    "The user name, used to login"

    _password = Column(
        password_t, name='password',
        default='*', nullable=False,
        info=dict(
            label=_('Password'),
            hint=_('Login password of the user'),
            )
        )
    "Password of the user, kept crypted within the database"

    first_name = Column(
        shortstring_t,
        nullable=False,
        info=dict(
            label=_('First Name'),
            hint=_('First name of the user'),
            )
        )
    "First name of the user"

    last_name = Column(
        shortstring_t,
        nullable=False,
        info=dict(
            label=_('Last Name'),
            hint=_('Last name of the user'),
            )
        )
    "Last name of the user"

    email = Column(
        shortstring_t,
        info=dict(
            label=_('E-Mail'),
            hint=_('The e-mail address of the user'),
            ),
        )
    "The e-mail address of the user"

    last_login = Column(
        timestamp_t,
        info=dict(
            label=_('Last login'),
            hint=_('The time of the last successful login made by the user'),
            )
        )
    "Last time the user successfully logged in"

    last_password_change = Column(
        timestamp_t,
        info=dict(
            label=_('Last password change'),
            hint=_('The time when the user password was changed'),
            )
        )
    "Last time user changed his password"

    is_active = Column(
        boolean_t,
        default=True,
        nullable=False,
        info=dict(
            label=_('Active?'),
            hint=_('Whether this user is still active or not'),
            )
        )
    "Whether the user is still active or not"

    @hybrid_property
    def password(self):
        """Return the hashed password of the user."""

        return self._password

    @password.setter
    def password(self, raw_password):
        """Change the password of the user

        :param raw_password: the raw password, in clear
        """

        self._password = self.crypt.encode(raw_password)
        self.last_password_change = func.current_timestamp()

    def check_password(self, raw_password):
        """Check the password

        :param raw_password: the raw password, in clear
        :rtype: boolean

        Return ``True`` if the `raw_password` matches the user's
        password, ``False`` otherwise.
        """

        return self.is_active and self.crypt.check(self.password, raw_password)


__all__ = (
    "User",
    )
