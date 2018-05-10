import os
import sys

import PyPDF2
from PIL import Image

#TODO: Add in image recognition to recognize images using TensorFlow
# https://towardsdatascience.com/tensorflow-image-recognition-python-api-e35f7d412a70

# extracts the images from the pdfs and saves as a png
# change the save_folder on line 10
def extract_image(pageObj):
    save_folder = 'C:/users/ehofmann/desktop/'
    xObject = pageObj['/Resources']['/XObject'].getObject()

    for obj in xObject:
        if xObject[obj]['/Subtype'] == '/Image':
            size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
            data = xObject[obj].getData()
            if xObject[obj]['/ColorSpace'] == '/DeviceRGB':
                mode = "RGB"
            else:
                mode = "P"

            if xObject[obj]['/Filter'] == '/FlateDecode':
                img = Image.frombytes(mode, size, data)
                img.save(save_folder + obj[1:] + ".png")
            elif xObject[obj]['/Filter'] == '/DCTDecode':
                img = open(obj[1:] + ".jpg", "wb")
                img.write(data)
                img.close()
            elif xObject[obj]['/Filter'] == '/JPXDecode':
                img = open(obj[1:] + ".jp2", "wb")
                img.write(data)
                img.close()

pdfFileObj = open('C:/users/ehofmann/desktop/2017-q3/2017-07/P(1)0003117.pdf', 'rb')
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

for page in range(0,pdfReader.numPages):
    pageObj = pdfReader.getPage(page)

    #the below prints out the text of the PDF
    print(pageObj.extractText())
