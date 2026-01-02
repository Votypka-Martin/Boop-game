import time
import random

list = [0] * 65536

list2d = [[0] * 6] * 6

start = time.perf_counter()
dict = {}
for i in range(9216):
    dict[i] = i * 2
end = time.perf_counter()

print(f"Dictionary creation took {end - start:.6f} s")

def test_efficiency(func, *args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()

    elapsed = end - start
    print(f"Function '{func.__name__}' took {elapsed:.6f} s")

    return result, elapsed

def board_key(board, mask):
        return board & 65535

def list_test():
    mask = 65535
    for i in range(1000000):
        val = list[i & mask]

def dict_test():
    mask = 1 << 36 - 1
    for i in range(1000000):
        val = dict.get(i)

def num_ops_test():
    mask = 65535
    res = 0
    for j in range(1000000):
        res = mask + mask - mask * 2
    return res

def bit_ops_test():
    mask = 65535
    res = 0
    for j in range(1000000):
        res = mask | mask & mask ^ mask
    return res

def list2d_test():
    mask = 65535
    for i in range(1000000):
        val = list2d[0][1]

def mask_test():
    mask = 65535
    for i in range(1000000):
        val = mask & mask

test_efficiency(list2d_test)
test_efficiency(dict_test)