import random

from matplotlib import pyplot as plt


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


def plot_timings(esa_timings: dict[int, int], stree_timings: dict[int, int], file_name: str) -> None:
    x_esa = sorted(list(esa_timings.keys()))
    y_esa = []

    for key in x_esa:
        y_esa.append(esa_timings[key])

    x_stree = sorted(list(stree_timings.keys()))
    y_stree = []

    for key in x_stree:
        y_stree.append(stree_timings[key])

    plt.plot(x_esa, y_esa, label="ESA")
    plt.plot(x_stree, y_stree, label="Suffix Tree")

    plt.xlabel('pattern length')
    plt.ylabel('Time(s)')

    plt.title('ESA vs Suffix Tree runtime')

    plt.legend(loc="best")

    plot_file_name = "../../test/benchmark/results/" + file_name

    # save the plot in a file, to let tests finish
    plt.savefig(plot_file_name)
