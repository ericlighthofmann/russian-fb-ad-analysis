import os
import sys

import PyPDF2
from PIL import Image
import glob
import io
from tqdm import tqdm

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

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

master_pdf_list = []

def get_all_pdf_files():
    for (dirpath, dirnames, filenames) in os.walk(os.getcwd()):

        os.chdir(dirpath)
        all_pdfs = glob.glob('*.pdf')

        for pdf in tqdm(all_pdfs):

            #skip big files for testing purposes
            if os.path.getsize(pdf) > 3000000:
                continue
            # using PyPDF2 below, reads down the first column, then down the next column
            # this makes it hard to split words on
            # @fold
            def use_PyPDF2(page_size):
                pdf_file_obj = open(os.path.join(dirpath, pdf), 'rb')
                pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
                for page in range(0,pdf_reader.numPages):
                    page_obj = pdf_reader.getPage(page)
                    pdf_text = page_obj.extractText() + '\n'
                    pdf_text = " ".join(pdf_text.replace(u"\xa0", " ").strip().split())
                    uprint(pdf_text)
                    print ('--------------')
                    assert False

            # get the size of the PDF
            # @fold
            def get_page_size(pdf):
                pdf_file_obj = open(os.path.join(dirpath, pdf), 'rb')
                pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
                page_size = pdf_reader.getPage(0).mediaBox
                print (page_size)
                return page_size

            #try to use pdfminer.six to get text
            # @fold
            def use_pdfminer(pdf):
                rsrcmgr = PDFResourceManager()
                retstr = io.StringIO()
                codec = 'utf-8'
                laparams = LAParams()
                device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
                fp = open(pdf, 'rb')
                interpreter = PDFPageInterpreter(rsrcmgr, device)
                maxpages = 0
                caching = True
                pagenos = set()

                for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages,
                                              caching=caching,
                                              check_extractable=True):
                    interpreter.process_page(page)

                text = retstr.getvalue()
                fp.close()
                device.close()
                retstr.close()
                return text

            pdfminer_text = use_pdfminer(pdf)
            pdfminer_text = pdfminer_text.split('\n')
            pdfminer_text = [x for x in pdfminer_text if x != '']
            ad_targeting = ''
            for idx, p in enumerate(pdfminer_text):
                if p == 'Ad ID':
                    ad_id = pdfminer_text[idx+1]
                elif p == 'Ad Text':
                    ad_text = pdfminer_text[idx+1]
                elif p == 'Ad Landing Page':
                    ad_landing_page = pdfminer_text[idx+1].replace(' ','')
                elif p == 'Ad Targeting':
                    for sub_p in pdfminer_text[idx+1:]:
                        if sub_p != 'Ad Impressions':
                            ad_targeting += (' ' + sub_p)
                        else:
                            break
                elif p == 'Ad Impressions':
                    ad_impressions = pdfminer_text[idx+1]
                elif p == 'Ad Spend':
                    ad_spend = pdfminer_text[idx+1]
                elif p == 'Ad Creation Date':
                    ad_creation_date = pdfminer_text[idx+1]


            master_pdf_list.append(
                {
                    'ad_id': ad_id,
                    'ad_text': ad_text,
                    'ad_landing_page': ad_landing_page,
                    'ad_targeting': ad_targeting,
                    'ad_impressions': ad_impressions,
                    'ad_spend': ad_spend,
                    'ad_creation_date': ad_creation_date
                }
            )

home_dir = os.getcwd()
os.chdir('ads')

get_all_pdf_files()
