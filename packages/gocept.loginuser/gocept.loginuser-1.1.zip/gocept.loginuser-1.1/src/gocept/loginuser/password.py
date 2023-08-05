import bcrypt
import hashlib


WORK_FACTOR = 12  # 12=bcrypt default


HASH_FUNCTIONS = {
    'sha256': lambda plain, hashed: hashlib.sha256(plain).hexdigest(),
}


def check(plain, hashed):
    algorithm, sep, hashed_value = hashed.partition(':')
    if algorithm.lower() in HASH_FUNCTIONS:
        hash_fn = HASH_FUNCTIONS[algorithm.lower()]
        hashed = hashed_value
    else:
        hash_fn = bcrypt.hashpw
    plain = _encode(plain)
    hashed = _encode(hashed)
    return _constant_time_equal(hash_fn(plain, hashed), hashed)


def hash(plain):
    plain = _encode(plain)
    return unicode(bcrypt.hashpw(plain, bcrypt.gensalt(WORK_FACTOR)))


def _constant_time_equal(a, b):
    # adapted from <http://throwingfire.com/storing-passwords-securely/>,
    # see also <http://codahale.com/a-lesson-in-timing-attacks/>
    if len(a) != len(b):
        return False

    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)
    return result == 0


def _encode(text):
    if isinstance(text, unicode):
        text = text.encode('utf8')
    return text
