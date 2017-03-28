# based on a talk found here:
# https://youtu.be/M-UcUs7IMIM

import dis
import math
import collections
import time
import itertools


class Task:
    """
    Aggregates a co-routine and an integer id
    """
    next_id = 0

    def __init__(self, routine):
        self.id = Task.next_id
        Task.next_id += 1
        self.routine = routine


class Scheduler:

    def __init__(self):
        self.runnable_tasks = collections.deque()
        self.completed_task_results = {}
        self.failed_task_errors = {}

    def add(self, routine):
        task = Task(routine)
        self.runnable_tasks.append(task)
        return task.id

    def run_to_completion(self, futures=None):

        while len(self.runnable_tasks) > 0:
            if futures is not None:
                if not any(task.id in futures for task in self.runnable_tasks):
                    return

            task = self.runnable_tasks.popleft()
            # print('Running Task: {} ... '.format(task.id), end='')
            try:
                yielded = next(task.routine)
            except StopIteration as stopped:
                # print('Completed with result: {!r}'.format(stopped.value))
                self.completed_task_results[task.id] = stopped.value
            except Exception as e:
                # print('Failed with exception: {}'.format(e))
                self.failed_task_errors[task.id] = e
            else:
                assert yielded is None
                # print('Now Yielded')
                self.runnable_tasks.append(task)




def async_lucas():
    """
    Lucas sequence is infinite - showcases a generator object that involves 'some' computation.
    :return: 
    """
    yield 2
    a = 2
    b = 1
    while True:
        yield b
        a, b = b, a + b


def async_is_prime(x):
    """
    heavier computation infinite sequence.  Simple but inefficient 
    :return: 
    """
    if x < 2:
        return False
    for i in range(2, int(math.sqrt(x)) + 1):
        time.sleep(0.1)
        if x % i == 0:
            return False
        yield from async_sleep(0)
    return True


def async_search(iterable, async_predicate):
    for item in iterable:
        matches = yield from async_predicate(item)
        if matches:
            return item
    raise ValueError("Not Found!")


def async_print_matches(iterable, async_predicate):
    for item in iterable:
        matches = yield from async_predicate(item)
        if matches:
            print('Found :', item)


def async_sleep(interval_seconds):
    start = time.time()
    expiry = start + interval_seconds
    while True:
        yield
        now = time.time()
        if now >= expiry:
            break


def async_repetitive_message(message, interval_seconds):
    """
    yield control until a time interval expires.
    :param message: 
    :param interval_seconds: 
    :return: 
    """
    repeat = ['-', '\\', '|', '/']

    for switch in itertools.cycle(repeat):
        print('\r[{}] {}'.format(switch, message), end='')
        yield from async_sleep(interval_seconds)

if __name__ == "__main__":
    # Example of using a generator
    # for item in islice(lucas(), 10):
    #     print(item)

    #Example showing the stopiteration
    # items = async_search(lucas(), lambda x: x >= 10)
    # for x in range(10):
    #     next(items)

    # Example of scheduler
    # scheduler = Scheduler()
    # scheduler.add(async_search(lucas(), lambda x: len(str(x)) >= 6))
    # scheduler.add(async_search(lucas(), lambda x: len(str(x)) >= 20))
    # scheduler.run_to_completion()
    # scheduler.run_to_completion()

    # print(is_prime(12))
    # print(is_prime(13))
    # print(is_prime(2 ** 15-1))

    def async_some_numbers():
        for x in range(1500, 1600):
            yield x

    def async_compare_length(x):
        yield from async_sleep(0)
        if len(x) >= 5:
            return True
        return False

    # x = async_some_numbers()
    # print(dis.dis(x))

    scheduler = Scheduler()

    #task_00 = scheduler.add(async_print_matches(async_lucas(), async_is_prime))
    task_01 = scheduler.add(async_search(async_some_numbers(), async_is_prime))
    task_02 = scheduler.add(async_repetitive_message("Working ...", 0.25))
    scheduler.run_to_completion((task_01,))

    print()
    print(scheduler.completed_task_results)

