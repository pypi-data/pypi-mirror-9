# encoding=utf-8
from sqlalchemy import Column, Integer, String, DateTime
import gocept.loginuser.password


class InvalidLockReasonError(ValueError):

    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return "%s is not a valid lock reason." % self.reason


class User(object):

    LOCK_STATUS_MAXLOGINS = 'Zu viele fehlerhafte Login-Versuche'
    LOCK_STATUS_ADMIN = 'Gesperrt durch Administrator'

    username = Column(String(254), unique=True)
    encrypted_password = Column('password', String(80))

    failed_logins = Column(Integer, nullable=False, server_default='0')
    is_locked = Column(String(50), default=u'')
    last_login = Column(DateTime, nullable=True)

    @classmethod
    def create(cls, **kw):
        username = kw.get('username')
        if username is not None:
            kw['username'] = username.lower()
        return super(User, cls).create(**kw)

    @classmethod
    def by_username(cls, username):
        """Get a user by its unique username or `None`."""
        return cls.query().filter_by(username=username.lower()).first()

    @property
    def password(self):
        return self.encrypted_password

    @password.setter
    def password(self, value):
        self.encrypted_password = gocept.loginuser.password.hash(value)

    def check_password(self, plain):
        return gocept.loginuser.password.check(plain, self.password)

    @property
    def authenticated(self):
        return self.username is not None

    def lock(self, reason=None):
        """Lock a user because of `reason`.

           Reason can be:
               "MAXLOGINS": Too much unsuccessful login retries.
               "ADMIN": Locked by admin via admin ui.
        """
        reason_text = getattr(self, 'LOCK_STATUS_%s' % reason, None)
        if reason_text is None:
            raise InvalidLockReasonError(reason)
        self.is_locked = reason_text

    def unlock(self):
        """Unlock a user."""
        self.is_locked = None

    def __str__(self):
        return '<User %s>' % self.username
