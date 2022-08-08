import numpy as np
from algorithm3 import *

val = np.array([[67.0, 90.0, 86.0, 28.0, 44.0, 85.0, 28.0, 25.0], [5.0, 2.0, 27.0, 41.0, 82.0, 44.0, 28.0, 36.0], [55.0, 10.0, 46.0, 75.0, 61.0, 38.0, 85.0, 71.0]])
p = CouponProblem(3, 8)
p.valuation_matrix = val
r = coupon_allocation(p, debug=False, late_order=True)
