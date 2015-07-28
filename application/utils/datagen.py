import random
import string


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


def generate_inner_phone(already_used_numbers, start=7000, stop=9999):
    all_numbers = {number for number in range(start, stop)}
    unused_numbers = all_numbers - already_used_numbers
    return random.choice(tuple(unused_numbers))
