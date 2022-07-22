# Python program to create
# a pdf file

from PyPDF2 import PdfFileReader
from fpdf import FPDF
import matplotlib.pyplot as plt

# save FPDF() class into a
# variable pdf
pdf = FPDF()
# Add a page
pdf.add_page()

# set style and size of font
# that you want in the pdf
pdf.set_font("Arial", size=15)
# create a cell
# pdf.set_text_color(200, 50, 100)
# pdf.cell(200, 10, txt="GeeksforGeeks",
#          ln=1, align='C')
pdf.set_text_color(0, 50, 100)
pdf.write(10, "GeeksforGeeks\n")
pdf.set_text_color(200, 50, 100)
pdf.write(10, "GeeksforGeeks\n")

# add another cell
a = [1,2,3]
pdf.cell(200, 10, txt=a.__str__(),
         ln=2, align='C')

f = plt.figure()
plt.plot(range(10), range(10), "o")
plt.show()
f.savefig("test.png")
pdf.image('test.png',w = 150)
pdf.image('test.png',w = 150)
# save the pdf with name .pdf
pdf.output("GFG.pdf")
