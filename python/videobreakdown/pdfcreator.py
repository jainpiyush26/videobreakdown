#!/usr/bin/env python
# std import
from fileinput import filename
import os
from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes

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
                                   pagesize=(width, height))

        return canvas_obj



data = PdfCreator({}, "")
data._create_canvas()