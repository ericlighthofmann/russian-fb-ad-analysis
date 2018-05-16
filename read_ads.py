import os
import sys

import PyPDF2
from PIL import Image
import glob
import minecart

#TODO: Add in image recognition to recognize images using TensorFlow
# https://towardsdatascience.com/tensorflow-image-recognition-python-api-e35f7d412a70

#TODO: Figure out how to parse the data correctly and add the data into a Postgres database
#using Django

# @fold
def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    '''print function to print to console without encoding errors,
    dunno how it works, stole from SO'''
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)

# @fold
def extract_image(pageObj):

    '''
    Extracts the fb ad image from each of the PDFs and saves it as a .png file. Need to change
    the save_folder...maybe by where the PDF itself is saved.
    '''

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

def get_all_pdf_files():
    for (dirpath, dirnames, filenames) in os.walk(os.getcwd()):
        os.chdir(dirpath)
        all_pdfs = glob.glob('*.pdf')
        for pdf in all_pdfs:
            pdf_dict = {
            'ad_id': '',
            'ad_text': '',
            'ad_landing_page': '',
            'ad_targeting': '',
            'ad_impressions': '',
            'ad_clicks': '',
            'ad_spend': '',
            'ad_creation_date': '',
            }
            #print (os.path.join(dirpath, pdf))

            # using PyPDF2 below, reads down the first column, then down the next column
            # this makes it hard to split words on
            def use_PyPDF2():
                pdf_file_obj = open(os.path.join(dirpath, pdf), 'rb')
                pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
                for page in range(0,pdf_reader.numPages):
                    page_obj = pdf_reader.getPage(page)
                    pdf_text = page_obj.extractText() + '\n'
                    pdf_text = " ".join(pdf_text.replace(u"\xa0", " ").strip().split())
                    uprint(pdf_text)
                    print ('--------------')
                    assert False
            #use_PyPDF2()

            def get_page_size(pdf):
                pdf_file_obj = open(os.path.join(dirpath, pdf), 'rb')
                pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
                page_size = pdf_reader.getPage(0).mediaBox
                return page_size

            page_size = get_page_size(pdf)
            print (page_size)

            # using minecart below which seems to be able to split PDFs into certain
            # vectors or boxes. Might make reading the columns easier.

home_dir = os.getcwd()
os.chdir('ads')
get_all_pdf_files()
