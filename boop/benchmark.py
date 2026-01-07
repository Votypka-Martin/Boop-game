import time
import random

list = [0] * 65536

list2d = [[random.randint(0, 4) for _ in range(6)] for _ in range(6)]

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
    for i in range(1000000):
        val = [i, i , i , i]

def dict_test():
    for i in range(1000000):
        val = dict.get(i)

def num_ops_test():
    mask = 65535
    res = 0
    for j in range(1000000):
        res = mask + mask - mask * 2 + mask / 2 + mask % 2
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
        for j in range(6):
            for k in range(6):
                if list2d[j][k] != 0:
                    val = list2d[j][k]

def mask_test():
    mask = 65535
    for i in range(1000000):
        val = mask & mask
    
def tuple_test():
    for i in range(1000000):
        val = (i, i, i, i)

def big_int_test():
    dict = {}
    for i in range(1000000):
        dict[i | i << 36 | i << 72 | i << 108] = (i, i, i)

test_efficiency(tuple_test)
test_efficiency(list_test)
test_efficiency(dict_test)