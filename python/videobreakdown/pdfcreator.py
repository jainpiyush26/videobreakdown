#!/usr/bin/env python
# std imports
from fileinput import filename
import os

# third party imports
from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes
from reportlab.lib.units import mm
from reportlab.lib.colors import darkblue, gray, black

# internal imports
from base import get_config

class PdfCreator(object):
    """_summary_

    :param object: _description_
    :type object: _type_
    """
    def __init__(self, video_details, export_path):
        """_summary_

        :param prop_dict: _description_
        :type prop_dict: _type_
        :param thumbnail_path: _description_
        :type thumbnail_path: _type_
        :param export_path: _description
        :type export_path: _type_
        """
        self.video_details = video_details
        self.export_path = export_path
        self.config = get_config()

    def _create_canvas(self):
        """_summary_

        :raises RuntimeError: _description_
        :raises RuntimeError: _description_
        :return: _description_
        :rtype: _type_
        """
        # Logic to get the correct size of the PDF
        # we want to export
        pdf_size = self.config.get("pdf").get("size")
        pdf_orn = self.config.get("pdf").get("orientation")
        # We can store the pdf size as a default string
        # or can use custom height,width list input in config
        if isinstance(pdf_size, str):
            _size_tuple = getattr(pagesizes, pdf_size)
            if pdf_orn == "landscape":
                width, height = _size_tuple[1], _size_tuple[0]
            else:
                width, height = _size_tuple[0], _size_tuple[1]
        elif isinstance(pdf_size, list):
            width, height = pdf_size[0], pdf_size[1]
        else:
            raise RuntimeError("Invalid pdf size format"
                               " {0}".format(pdf_size))

        # We check to ensure the PDF path does not already exists, we do not
        # want to overwrite it.
        if os.path.exists(self.export_path):
            raise RuntimeError("PDF path {0} already"
                               " exists!".format(self.export_path))

        canvas_obj = canvas.Canvas(filename=self.export_path,
                                   pagesize=(width, height),
                                   bottomup=0)

        return canvas_obj


path = "/Users/piyush/Documents/PersonalFolders/coding_work/pdf_creation_test/001.pdf"
if os.path.exists(path):
    os.remove(path)
data = PdfCreator({}, path)
canvas = data._create_canvas()

sample_dict = {'xxhash-64': '1a9990ea6f727531',
               'Size': '220 MiB',
               'Format': 'MOV',
               'Created': '2022:02:17 17:03:05',
               'Resolution': '3840x2160',
               'Encoding': 'hvc1',
               'FPS': 29.97,
               'Duration': '18.49 s',
               'Frames': 554}

def test_this(canvas, x, y):
    print ("Starting y size ", y)
    if (y > pagesizes.A4[0]):
        canvas.showPage()
        y = 10 * mm
    canvas.setTitle("This is a test")
    canvas.setAuthor("pjain")
    key_font = 'Helvetica-Bold'
    value_font = 'Helvetica'
    title_size = 12
    size=10
    canvas.setFont(key_font, title_size)
    canvas.setFillColor(darkblue)
    canvas.drawString(x, y, "20220217_DOC_2785.MP4")
    y = y+6*mm
    print ("Title y size", y)
    if (y > pagesizes.A4[0]):
        canvas.showPage()
        y = 10*mm
    for key, value in sample_dict.items():
        canvas.setFillColor(black)
        canvas.setFont(value_font, size)
        canvas.drawString(x+10, y, str(value))
        canvas.setFillColor(gray)
        canvas.setFont(key_font, size)
        canvas.drawRightString(x, y, key + ":")
        y = y + 4.5*mm
        if (y > pagesizes.A4[0]):
            canvas.showPage()
            y = 10*mm
    return y
print (pagesizes.A4)
x = 25 * mm
y = 10 * mm
y = test_this(canvas, x, y)
y = y + 5*mm
y = test_this(canvas, x, y)
y = y + 5*mm
y = test_this(canvas, x, y)
y = y + 5*mm
y = test_this(canvas, x, y)
y = y + 5*mm
y = test_this(canvas, x, y)
y = y + 5*mm
y = test_this(canvas, x, y)

canvas.save()