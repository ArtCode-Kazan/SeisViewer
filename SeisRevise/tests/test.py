import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


x=np.array([1,2,3,4,5,6,7])
y=np.array([1,2,3,4,5,6,7])

mpl.rcParams['figure.subplot.left'] = 0.03
mpl.rcParams['figure.subplot.right'] = 0.97
mpl.rcParams['figure.subplot.bottom'] = 0.05
mpl.rcParams['figure.subplot.top'] = 0.95
#mpl.rcParams['figure.subplot.hspace'] = 0.2
#mpl.rcParams['figure.subplot.wspace'] = 0.2
#mpl.rcParams['figure.subplot.hspace'] = 0.05
#mpl.rcParams['figure.subplot.wspace'] = 0.05

fig = plt.figure()
fig.set_size_inches(16,9)

axes = fig.add_subplot(111)

axes.plot(x,y,label='Sum of Cause Fractions')

plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.show()

