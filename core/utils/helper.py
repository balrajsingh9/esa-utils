import random


def gen_random_substring(s: str, length: int) -> str:
    """
    :param s: the full original text from which the substrings will be generated
    :param length: the length of the sub
    :return: a random substring of length :param length
    """
    rand_idx = random.randrange(0, len(s) - length + 1)

    return s[rand_idx: rand_idx + length]


def gen_random_substrings(s: str, min_l: int = 0, max_l: int = 0, n: int = 0) -> list[str]:
    rand_substrings: list[str] = []

    for i in range(n):
        rand_l = random.randrange(min_l, max_l)
        rand_substrings.append(gen_random_substring(s, rand_l))

    return rand_substrings


