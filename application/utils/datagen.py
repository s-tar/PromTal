import random
import string

from sqlalchemy import func
from sqlalchemy.orm import load_only

from application.models.user import User
from application import db


def generate_password(length=8):
    password = ''.join((random.choice(string.ascii_lowercase) for _ in range(length)))
    already_used_indices = set()

    for _ in range(random.randint(1, 3)):
        index = random.choice(range(length))
        while index in already_used_indices:
            index = random.choice(range(length))
        already_used_indices.add(index)
        password = password[:index] + password[index].upper() + password[index + 1:]

    for _ in range(random.randint(1, 3)):
        index = random.choice(range(length))
        while index in already_used_indices:
            index = random.choice(range(length))
        already_used_indices.add(index)
        password = password[:index] + str(random.choice(string.digits)) + password[index + 1:]

    return password


# def generate_inner_phone(already_used_numbers, begin, end):
#     all_numbers = {number for number in range(begin, end)}
#     unused_numbers = all_numbers - already_used_numbers
#
#     return str(random.choice(tuple(unused_numbers))) if len(unused_numbers) != 0 else None


def generate_inner_phone(begin, end):
    inner_phone = int(db.session.query(func.max(User.inner_phone)).filter(User.inner_phone.like('____')).scalar()) + 1
    return inner_phone if inner_phone in range(begin, end) else None
