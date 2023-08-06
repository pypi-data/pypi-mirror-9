from PIL import Image
from datetime import datetime

data = {}

def mandelbrot(args):
    row = args[0]
    col = args[1]
    size_x = args[2]
    size_y = args[3]
    # data = args[4]
    global data

    ret = [ 0.0 ] *3

    x0 = float(row) / size_x * 3.5 - 2.5
    y0 = float(col) / size_y * 2.0 - 1.0
    assert -2.5 <= x0 <= 1
    assert -1 <= y0 <= 1
    x = 0
    y = 0
    iteration = 0
    max_iteration = 1000
    while (x*x + y*y) < 4 and (iteration < max_iteration):
        xtemp = x*x - y*y + x0
        y = 2*x*y + y0
        x = xtemp
        iteration = iteration + 1
        color = iteration % 255
        #print(iteration, color)
        data[(row, col, 0)]  = color 
        data[(row, col, 1)] = (color + 75) % 255
        data[(row, col, 2)] = (color + 150) % 255
        # arr[(row, col, 0)] = color
        # arr[(row, col, 1)] = (color + 75) % 255
        # arr[(row, col, 2)] = (color + 150) % 255
    # return (ret[0], ret[1], ret[2])

def save_png(filename, data_map, size_x, size_y):
    im = Image.new('RGB', (size_x, size_y))
    pixels1 = im.load()
    for i in xrange(size_x):
        for j in xrange(size_y):
                pixels1[i, j] = (data_map[(i, j, 0)], data_map[(i,j,1)], data_map[(i,j,2)])
    im.save(filename, "PNG")

def par_for(f, *args):
    from itertools import product
    from multiprocessing import Pool
    p = Pool(4)

    p.map(f,[e for e in product(*args)])

    # def ret(l):
    #     from multiprocessing import Pool
    #     p = Pool(4)
    #     tmp = p.map(f, l)
    #     return tmp
    # return ret

def fast_mandelbrot(size_x, size_y):
    # from multiprocessing import Pool
    # p = Pool(4)
    # tmp = p.map(mandelbrot, [ (i, j, size_x, size_y) for i in xrange(size_x) for j in xrange(size_y) ])
    # data_map = {}
    # for i in xrange(size_x):
    #     for j in xrange(size_y):
    #         data_map[(i, j)] = tmp[i*size_y +j]
    # return data_map
    # tmp = par(mandelbrot)([(i, j, size_x, size_y) for i in range(size_x) for j in range(size_y)])
    
    # data_map = {}
    # for i in xrange(size_x):
    #     for j in xrange(size_y):
    #         data_map[(i, j)] = tmp[i*size_y +j]
    # return data_map    
    par_for(mandelbrot, xrange(size_x), xrange(size_y), [size_x], [size_y])
    
    # print data_map

    # return data_map

def slow_mandelbrot(size_x, size_y):
    # arr = numpy.zeros(dtype=numpy.int8, shape=(size_x, size_y, 3))
    # arr = [[0, 0, 0] for i in range()]
    data = {}
    for row in range(size_x):
        for col in range(size_y):
            mandelbrot((row, col, size_x, size_y))

        # if row == col:
        # arr[row, col, 0] = 255
        # return arr    
        # for x in []:
            # x0 = float(row) / size_x * 3.5 - 2.5
            # y0 = float(col) / size_y * 2.0 - 1.0
            # assert -2.5 <= x0 <= 1
            # assert -1 <= y0 <= 1
            # x = 0
            # y = 0
            # iteration = 0
            # max_iteration = 1000
            # while (x*x + y*y) < 4 and (iteration < max_iteration):
            #     xtemp = x*x - y*y + x0
            #     y = 2*x*y + y0
            #     x = xtemp
            #     iteration = iteration + 1
            #     color = iteration % 255
            #     #print(iteration, color)
            #     arr[(row, col, 0)] = color
            #     arr[(row, col, 1)] = (color + 75) % 255
            #     arr[(row, col, 2)] = (color + 150) % 255
    return data

if __name__ == "__main__":
    size_x, size_y = 500, 500
    filename = "mandelbrot.png"
    # slow version
    start = datetime.now()
    # data_map = slow_mandelbrot(size_x, size_y)
    slow_mandelbrot(size_x, size_y)
    data_map = data
    end = datetime.now()
    print "slow: runtime: %s" % str(end-start)
    save_png(filename, data_map, size_x, size_y)

    # multi-process version
    start = datetime.now()
    # data_map = fast_mandelbrot(size_x, size_y)
    fast_mandelbrot(size_x, size_y)
    data_map = data
    end = datetime.now()
    print "fast: runtime: %s" % str(end-start)
    save_png("mp-"+filename, data_map, size_x, size_y)    
