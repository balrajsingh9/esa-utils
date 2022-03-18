from __future__ import annotations


class Node:
    def __init__(self, data):
        self.__data = data
        self.__next = None

    def get_data(self):
        return self.__data

    def get_next(self):
        return self.__next

    def set_data(self, data):
        self.__data = data

    def set_next(self, nextNode):
        self.__next = nextNode


class LinkedList:
    def __init__(self):
        self.head = None


class Interval:
    def __init__(self, lcp_value: int = 0, lb: int = 0, rb: int = -1, child_list=None):
        if child_list is None:
            child_list = []
        self.__lcp_value: int = lcp_value
        self.__lb: int = lb
        self.__rb: int = rb
        self.__child_list = child_list
        self.__pos_sets = None

    def get_lcp_value(self):
        return self.__lcp_value

    def get_lb(self):
        return self.__lb

    def get_rb(self):
        return self.__rb

    def get_child_list(self):
        return self.__child_list

    def get_pos_sets(self):
        return self.__pos_sets

    def update_child_list(self, interval):
        self.__child_list.append(interval)

    def set_lb(self, lb: int):
        self.__lb = lb

    def set_rb(self, rb: int):
        self.__rb = rb

    def set_lcp_value(self, lcp_value: int):
        self.__lcp_value = lcp_value

    def set_pos_sets(self, pos_sets):
        self.__pos_sets = pos_sets

    def __str__(self):
        return f"lb=%s, rb=%s, lcp_value=%s" % (self.__lb, self.__rb, self.__lcp_value)


def add(top_interval: Interval, last_interval: Interval):
    top_interval.update_child_list(last_interval)


class SpecialStack:
    def __init__(self):
        self.__stack = []
        self.__len: int = 0

    def top(self):
        if self.__len <= 0:
            return None
        else:
            return self.__stack[self.__len - 1]

    def pop(self):
        self.__len -= 1
        return self.__stack.pop()

    def push(self, interval: Interval):
        self.__stack.append(interval)
        self.__len += 1

    def get_size(self):
        return self.__len

    def is_empty(self):
        return self.__len == 0


def process(lcp_interval: Interval, suf_tab, s):
    pos_set_list = LinkedList()
    prev = None

    pos_set = []
    l = lcp_interval.get_lcp_value()

    for j in range(0, len(lcp_interval.get_child_list())):
        pos_set = [-1] * 26
        child_interval: Interval = lcp_interval.get_child_list()[j]
        p_set = set()
        lb = child_interval.get_lb()
        rb = child_interval.get_rb()

        for i in range(lb, rb + 1):
            p_set.add(suf_tab[i])

        for i in range(0, 26):
            for p in p_set:
                if p != 0 and (s[p - 1] == chr(i + 97)):
                    pos_set[i] = p

        if pos_set_list.head is None:
            pos_set_list.head = Node(pos_set)
            prev = pos_set_list.head
        else:
            new_node = Node(pos_set)
            new_node.set_next(prev.get_next())
            prev.set_next(new_node)
            prev = new_node

        curr = pos_set_list.head

        while curr is not None:
            last_pos_set = curr.get_data()

            for i in range(0, 26):
                for k in range(0, 26):
                    p = last_pos_set[i]
                    if i != k and last_pos_set[i] != -1 and pos_set[k] != -1:
                        p_prime = pos_set[k]

                        if p < p_prime:
                            print(f"(%s, %s), (%s, %s)" % (
                                p, p + l - 1, p_prime, p_prime + l - 1))

            curr = curr.get_next()

    lcp_interval.set_pos_sets(pos_set_list)


def perform_bottom_up_traversal(s, suftab, lcp_table):
    last_interval: Interval | None = None
    stack: SpecialStack = SpecialStack()

    stack.push(Interval())

    for i in range(1, len(lcp_table)):
        lb = i - 1
        top: Interval = stack.top()

        while lcp_table[i] < top.get_lcp_value():
            top.set_rb(i - 1)
            last_interval: Interval = stack.pop()

            process(last_interval, suftab, s)

            lb: int = last_interval.get_lb()
            top = stack.top()

            if lcp_table[i] <= top.get_lcp_value():
                top.update_child_list(last_interval)
                last_interval = None

        if lcp_table[i] > top.get_lcp_value():
            if last_interval is not None:
                stack.push(Interval(lcp_table[i], lb, -1, [last_interval]))
                last_interval = None
            else:
                stack.push(Interval(lcp_table[i], lb, -1, []))

    stack.top().set_rb(len(lcp_table) - 1)
    process(stack.pop(), suftab, s)
