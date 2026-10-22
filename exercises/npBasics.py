#32, 3, 224, 224) Those are 4 dimensions, 32 images, with 3 coluor channels per pixel, 224 by 224 in size. The 32 images are stacked together in a batch, and each image has 3 channels (red, green, blue) and is 224 pixels wide and 224 pixels tall.
import numpy as np
zero = np.zeros((3,4)) # you are calling a function zeros and passing a tuple (3, 4). colums rows.
#It is needed because you need memory before you fill it.
ones = np.ones((3,4))
eye = np.eye(4)
print(zero)
print(ones)
print(eye)
arange = np.arange(0, 10, 2)
print(arange)# start at 0, go up to 10, but don't include 10, and increment by 2 each time.produces a numpy array.
linspace = np.linspace(0, 1, 5) # start at 0, go up to 1, and create 5 evenly spaced numbers between them.
print(linspace)
rng = np.random.default_rng(seed =42) # create a random number generator with a seed of 42. The seed is used to initialize the random number generator, so that you get the same random numbers each time you run the c random number code.If you dont seed you get different random numbers each time.
print(rng.random((3,4))) # generate a 3 by 4 array of random numbers between 0 and 1.
normal_bell_curve_center_zero= rng.standard_normal((3,3))
print(normal_bell_curve_center_zero) # generate a 3 by 3 array of random numbers from a standard normal distribution (mean = 0, std = 1). std how far you are from the mean. Mean 0 means that most values are towards near 0 with fewer values further away from 0.
# Python list -> flexible collection of Python objects.
# NumPy array (ndarray) -> contiguous block of values, all with the same dtype.
# dtype -> determines the type and memory used by each element.
# shape -> describes the structure of the data (rows, columns, etc.).
# Everything in AI-images, text embeddings, neural network weights, 
# activations-is ultimately represented as arrays/tensors with a shape and a dtype.
a = np.array([23, 16, 47, 87, 45, 36])
print(a[2])
print(a[-2])
print(a[1:4]) # slicing, start at index 1, go up to but not including index 4.