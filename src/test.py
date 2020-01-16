import numpy as np
import matplotlib.pyplot as plt

a = np.zeros((2,5))
a[1,0] = 1
plt.imshow(a, cmap='gray')
plt.show()