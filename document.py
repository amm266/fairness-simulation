import numpy as np
from fpdf import FPDF

from algorithm3 import coupon_allocation
from simulation import CouponProblem

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=15)
val = [[0.12607449856733524, 0.06303724928366762, 0.1318051575931232, 0.24068767908309452, 0.03724928366762178,
        0.10028653295128939, 0.13467048710601717, 0.16618911174785098],
       [0.19047619047619047, 0.0047619047619047615, 0.08333333333333333, 0.13809523809523808, 0.08095238095238096,
        0.11666666666666665, 0.15952380952380954, 0.22619047619047616],
       [0.19680851063829785, 0.19148936170212763, 0.2473404255319149, 0.0, 0.2127659574468085, 0.0026595744680851063,
        0.03723404255319149, 0.11170212765957446]]

p = CouponProblem(3, 8, valuation=val)
r = coupon_allocation(p, debug=True, pdf=pdf, late_order=False)
print(r)
pdf.output("instance-fail.pdf")
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=15)
p = CouponProblem(3, 8, valuation=val)
r = coupon_allocation(p, debug=True, pdf=pdf, late_order=True)
pdf.output("instance-success.pdf")
print(r)