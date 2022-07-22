import numpy as np
from fpdf import FPDF

from algorithm4 import delgo_coupon_allocation
from simulation import CouponProblem
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=15)
# alloc1 = np.array([[0.13533835, 0.00451128, 0.0887218, 0.08421053, 0.1443609, 0.13834586, 0.11278195, 0.10075188, 0.09323308,
#            0.09774436],
#           [0.17391304, 0.08237986, 0.0617849, 0.09839817, 0.13501144, 0.0389016, 0.0389016, 0.10983982, 0.03661327,
#            0.22425629]
#     , [0.1, 0.04923077, 0.15230769, 0.05230769, 0.13538462, 0.07230769, 0.15384615, 0.11846154, 0.11230769, 0.05384615],
#           [0.12562814, 0.06867672, 0.14070352, 0.15745394, 0.13232831, 0.06197655, 0.12227806, 0.02345059, 0.12730318,
#            0.04020101] ])
p = CouponProblem(4, 10)
# p.valuation_matrix = alloc1
r = delgo_coupon_allocation(p, debug=True, pdf=pdf)
pdf.output("instance.pdf")