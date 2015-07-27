import random
import string


def generate_password(length=8):
    password = ''.join((random.choice(string.ascii_lowercase) for _ in range(length)))

    for amount in range(random.randint(1, 3)):
        for _ in range(amount):
            index = random.choice(range(length))
            password = password[:index] + password[index].upper() + password[index + 1:]

    for amount in range(random.randint(1, 3)):
        for _ in range(amount):
            index = random.choice(range(length))
            password = password[:index] + str(random.choice(string.digits)) + password[index + 1:]

    return password


def generate_inner_number(already_used_numbers, init=6000, length=4):
    all_numbers = set()
    for number in range(init, int('9' * length)):
        all_numbers.add(number)
    unused_numbers = all_numbers - already_used_numbers
    return random.choice(tuple(unused_numbers))
