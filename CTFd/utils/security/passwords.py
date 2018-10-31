from passlib.hash import bcrypt_sha256
import hashlib


def hash_password(p):
    return bcrypt_sha256.encrypt(p.encode('utf-8'))


def check_password(p, hash):
    return bcrypt_sha256.verify(p.encode('utf-8'), hash)


def sha256(p):
    return hashlib.sha256(p.encode('utf-8')).hexdigest()