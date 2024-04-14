import asyncio
import math

import numpy as np
from PIL import Image


async def calculate_avg_brightness_task(name):
    img = Image.open(name)
    arr = np.asarray(img)

    width, heigth = img.size  # ширина (x) и высота (y) изображения
    matrix = []
    for i in range(heigth):
        matrix.append([0] * width)

    for h in range(heigth):
        for w in range(width):
            r, g, b = arr[h, w]
            matrix[h][w] = int(r) + int(g) + int(b)

    avg = np.mean(matrix)
    size = np.size(matrix)
    return (arr, np.array(matrix), avg, size)


# считаем процент пикселей ярче среднего и чаще всего встречающегося среди всех пикселей
async def calculate_percent_task(name, arr, matrix, avg, size):
    flatList = np.concatenate(arr)
    maskList = np.concatenate(matrix > avg)
    unique_colors, counts = np.unique(flatList[maskList], return_counts=True, axis=0)
    most_frequent_index = np.argmax(counts)
    percentvalue = counts[most_frequent_index] / size * 100
    percent = math.floor(percentvalue * 1000)
    print(f"Done {name}, percent {percent}")
    return percent


async def calculate_amount_task(name, npmatrix, avg, size):
    arr = npmatrix[(npmatrix > avg)]
    amount = math.floor((len(arr) * 100) / size)
    print(f"Done {name}, amount {amount}")
    return amount


async def calculate_quarter_task(name, npmatrix, avg):
    if npmatrix.shape[0] % 2 != 0:
        row = [0] * npmatrix.shape[1]
        npmatrix = np.row_stack([row, npmatrix])

    if npmatrix.shape[1] % 2 != 0:
        col = [0] * npmatrix.shape[0]
        npmatrix = np.column_stack([col, npmatrix])

    verticals = np.vsplit(npmatrix, 2)
    tophorizonts = np.hsplit(verticals[0], 2)
    bottomhorizonts = np.hsplit(verticals[1], 2)

    result = {
        'I': np.count_nonzero(tophorizonts[1] > avg),
        'II': np.count_nonzero(tophorizonts[0] > avg),
        'III': np.count_nonzero(bottomhorizonts[0] > avg),
        'IV': np.count_nonzero(bottomhorizonts[1] > avg)
    }

    res = sorted(result.items(), key=lambda x: (-x[1], x[0]))
    quarter = res[0][0]
    print(f"Done {name}, quarter {quarter}")
    return quarter


async def execute_image_task(name):
    local_tasks = []
    print(f"Start {name}")

    pixels, matrix, avg, size = await calculate_avg_brightness_task(name)
    local_tasks.append(calculate_percent_task(name, pixels, matrix, avg, size))
    local_tasks.append(calculate_amount_task(name, matrix, avg, size))
    local_tasks.append(calculate_quarter_task(name, matrix, avg))

    result = await asyncio.gather(*local_tasks)
    percent = result[0]
    amount = result[1]
    quarter = result[2]
    print(f"Ready {name}")
    return (name, percent, amount, quarter)


async def asteroids(*data):
    tasks = []
    for name in data:
        tasks.append(execute_image_task(name))
    return await asyncio.gather(*tasks)


data = ['1.jpg', '2.jpg', '3.jpg']
# data = ['1.jpg']
print(asyncio.run(asteroids(*data)))
