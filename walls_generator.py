import random

def generate_level():
    quantity_x = random.randint(3, 6)
    ret_arr = []
    x_mem = 0
    for y in range(0, 10):
        for line_x in range(0, quantity_x):
            x = random.randint(0, 9)
            if x == x_mem:
                break
            x_mem = x
            ret_arr.append([x, y])
    return ret_arr
    #print(ret_arr, print(len(ret_arr)))

#print(generate_level())
