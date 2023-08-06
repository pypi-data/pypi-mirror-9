# passwords.py

r'''Handles password hashing
'''

import base64
import hashlib
import hmac

from passlib.context import CryptContext
from flask import current_app


def get_cryptcontext(app):
    pw_hash = app.config['PASSWORD_HASH']
    schemes = app.config['PASSWORD_SCHEMES']
    deprecated = app.config['DEPRECATED_PASSWORD_SCHEMES']
    if pw_hash not in schemes:
        raise ValueError("Invalid PASSWORD_HASH setting, "
                         "must be in PASSWORD_SCHEMES")
    if pw_hash in deprecated:
        raise ValueError("Invalid PASSWORD_HASH setting, "
                         "must not be in DEPRECATED_PASSWORD_SCHEMES")
    return CryptContext(schemes=schemes, default=pw_hash, deprecated=deprecated)

def get_pwd_context():
    pwd_context = current_app.get('dry_pwd_context')
    if pwd_context is None:
        print("creating pwd_context on app")
        pwd_context = get_cryptcontext(current_app)
        current_app.dry_pwd_context = pwd_context
    return pwd_context

def verify_and_update_password(password, member):
    r'''Adapted from Flask Security.

    Return True if the password is valid.
    '''
    pwd_context = get_pwd_context()
    if pwd_context.identify(member.password) == 'plaintext':
        if pwd_context.verify(password, member.password):
            if pwd_context.needs_update(member.password):
                member.password = hash_password(password)
            return True
        return False

    password = get_hmac(password)
    verified, new_password = pwd_context.verify_and_update(password,
                                                           member.password)
    if verified and new_password:
        member.password = new_password

    return verified

def get_hmac(password):
    r'''Adapted from Flask Security.
    '''
    salt = current_app.config['PASSWORD_SALT']
    h = hmac.new(salt.encode('utf-8'), password.encode('utf-8'), hashlib.sha512)
    return base64.b64encode(h.digest())


def hash_password(password):
    if current_app.config['PASSWORD_HASH'] == 'plaintext':
        return password
    #signed = get_hmac(password).decode('ascii')
    signed = get_hmac(password)
    return get_pwd_context().encrypt(signed)

