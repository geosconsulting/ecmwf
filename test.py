import numpy as np

randomico = np.random.rand(8,6)
print randomico

print randomico.size
print randomico.shape

ulX_1 = 2
lrX_1 = 5
ulY_1 = 1
lrY_1 = 4

sub_randomico = randomico[ulX_1:lrY_1,ulY_1:lrY_1]
print sub_randomico