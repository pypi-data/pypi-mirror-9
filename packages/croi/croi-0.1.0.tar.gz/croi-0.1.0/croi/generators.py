import random
import re
import collections

# ----------------------------------------------------------------------------
# Base Generators
# ----------------------------------------------------------------------------


def forever(initial=0, step=1):
    x = initial
    while True:
        yield x
        x += step


def build(factory):
    while True:
        yield factory()


def duplicate(anything):
    while True:
        yield anything


def zeros():
    while True:
        yield 0


def ones():
    while True:
        yield 1


def random_ints(start=0, end=1):
    while True:
        yield random.randint(start, end)


def random_floats(start=0.0, end=1.0):
    while True:
        yield random.uniform(start, end)


# ----------------------------------------------------------------------------
# Take
# ----------------------------------------------------------------------------


def take(n_or_predicate, iterable):
    if callable(n_or_predicate):
        for x in take_while(n_or_predicate, iterable):
            yield x

    else:
        for x in take_n(n_or_predicate, iterable):
            yield x


def take_n(n, iterable):
    i = 0
    for x in iterable:
        i += 1
        if i > n:
            break
        yield x


def take_while(predicate, iterable):
    for x in iterable:
        if predicate(x):
            yield x
        else:
            break

# ----------------------------------------------------------------------------
# Drop
# ----------------------------------------------------------------------------


def drop(n_or_predicate, iterable):
    if callable(n_or_predicate):
        for x in drop_while(n_or_predicate, iterable):
            yield x

    else:
        for x in drop_n(n_or_predicate, iterable):
            yield x


def drop_n(n, iterable):
    i = 0
    for x in iterable:
        i += 1
        if i <= n:
            continue

        yield x


def drop_while(predicate, iterable):
    for x in iterable:
        if predicate(x):
            continue
        else:
            yield x


# ----------------------------------------------------------------------------
# Value Selectors
# ----------------------------------------------------------------------------


def nth(n, iterable):
    v = None
    for x in take_n(n, iterable):
        v = x

    return v


def head(iterable):
    for x in iterable:
        return x


def tail(iterable):
    skipped = False
    for x in iterable:
        if not skipped:
            skipped = True
            continue
        else:
            yield x


# ----------------------------------------------------------------------------
# Indexing
# ----------------------------------------------------------------------------


def index(needle, iterable):
    for i, x in enumerate(iterable):
        if x == needle:
            return i

    raise IndexError(needle)


def indexes(needle, iterable):
    for i, x in enumerate(iterable):
        if x == needle:
            yield i


# ----------------------------------------------------------------------------
# Filtering
# ----------------------------------------------------------------------------

def select(regex_or_needle_or_predicate, iterable):
    if callable(regex_or_needle_or_predicate):
        for x in select_where(regex_or_needle_or_predicate, iterable):
            yield x

    else:
        try:
            for x in select_match(regex_or_needle_or_predicate, iterable):
                yield x
            return

        except TypeError as err:
            if 'first argument' not in str(err):
                raise err
            else:
                pass

        for x in select_eq(regex_or_needle_or_predicate, iterable):
            yield x


def select_eq(needle, iterable):
    for x in iterable:
        if x == needle:
            yield x


def select_where(predicate, iterable):
    for x in iterable:
        if predicate(x):
            yield x


def select_match(regex, iterable):
    compiled = re.compile(regex)
    for x in iterable:
        if compiled.match(x) is not None:
            yield x


def reject(regex_or_needle_or_predicate, iterable):
    if callable(regex_or_needle_or_predicate):
        for x in reject_where(regex_or_needle_or_predicate, iterable):
            yield x

    else:
        try:
            for x in reject_match(regex_or_needle_or_predicate, iterable):
                yield x
            return

        except TypeError as err:
            if 'first argument' not in str(err):
                raise err
            else:
                pass

        for x in reject_eq(regex_or_needle_or_predicate, iterable):
            yield x


def reject_eq(needle, iterable):
    for x in iterable:
        if x != needle:
            yield x


def reject_where(predicate, iterable):
    for x in iterable:
        if not predicate(x):
            yield x


def reject_match(regex, iterable):
    compiled = re.compile(regex)
    for x in iterable:
        if compiled.match(x) is None:
            yield x


def partition(needle_or_predicate, iterable):
    if callable(needle_or_predicate):
        return partition_where(needle_or_predicate, iterable)

    else:
        try:
            return partition_match(needle_or_predicate, iterable)
        except TypeError as err:
            if 'first argument' not in str(err):
                raise err
            else:
                pass

        return partition_eq(needle_or_predicate, iterable)


def partition_eq(needle, iterable):
    left = collections.deque()
    right = collections.deque()
    iterator = iter(iterable)

    def selector():
        while True:
            if len(left) > 0:
                yield left.popleft()
            else:
                try:
                    item = iterator.next()
                    if item == needle:
                        yield item
                    else:
                        right.append(item)

                except StopIteration:
                    return

    def rejector():
        while True:
            if len(right) > 0:
                yield right.popleft()
            else:
                try:
                    item = iterator.next()
                    if item != needle:
                        yield item
                    else:
                        left.append(item)

                except StopIteration:
                    return

    return selector(), rejector()


def partition_where(predicate, iterable):
    left = collections.deque()
    right = collections.deque()
    iterator = iter(iterable)

    def selector():
        while True:
            if len(left) > 0:
                yield left.popleft()
            else:
                try:
                    item = iterator.next()
                    if predicate(item):
                        yield item
                    else:
                        right.append(item)

                except StopIteration:
                    return

    def rejector():
        while True:
            if len(right) > 0:
                yield right.popleft()
            else:
                try:
                    item = iterator.next()
                    if not predicate(item):
                        yield item
                    else:
                        left.append(item)

                except StopIteration:
                    return

    return selector(), rejector()


def partition_match(regex, iterable):
    compiled = re.compile(regex)
    left = collections.deque()
    right = collections.deque()
    iterator = iter(iterable)

    def selector():
        while True:
            if len(left) > 0:
                yield left.popleft()
            else:
                try:
                    item = iterator.next()
                    if compiled.match(item) is not None:
                        yield item
                    else:
                        right.append(item)

                except StopIteration:
                    return

    def rejector():
        while True:
            if len(right) > 0:
                yield right.popleft()
            else:
                try:
                    item = iterator.next()
                    if compiled.match(item) is None:
                        yield item
                    else:
                        left.append(item)

                except StopIteration:
                    return

    return selector(), rejector()
