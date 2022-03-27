#!/usr/bin/env python
# std imports
from fileinput import filename
import os

# third party imports
from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes
from reportlab.lib.units import mm
from reportlab.lib.colors import (darkblue,
                                  gray,
                                  black,
                                  lightblue)

# internal imports
from base import get_config, PdfConstants, USERNAME



class PdfCreator(object):
    """_summary_

    :param object: _description_
    :type object: _type_
    """
    def __init__(self, video_details, export_file_path):
        """_summary_

        :param prop_dict: _description_
        :type prop_dict: _type_
        :param thumbnail_path: _description_
        :type thumbnail_path: _type_
        :param export_path: _description
        :type export_path: _type_
        """
        self.video_details = video_details
        self.export_file_path = export_file_path
        self.config = get_config()
        self.width, self.height = 0, 0
        self.canvas_obj = None
        self.const = PdfConstants()

    def _create_canvas(self):
        """_summary_

        :raises RuntimeError: _description_
        :raises RuntimeError: _description_
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
                self.width, self.height = _size_tuple[1], _size_tuple[0]
            else:
                self.width, self.height = _size_tuple[0], _size_tuple[1]
        elif isinstance(pdf_size, list):
            self.width, self.height = pdf_size[0], pdf_size[1]
        else:
            raise RuntimeError("Invalid pdf size format"
                               " {0}".format(pdf_size))

        # We check to ensure the PDF path does not already exists, we do not
        # want to overwrite it.
        if os.path.exists(self.export_file_path):
            raise RuntimeError("PDF path {0} already"
                               " exists!".format(self.export_path))

        self.canvas_obj = canvas.Canvas(filename=self.export_file_path,
                                        pagesize=(self.width, self.height),
                                        bottomup=0)


    def _set_custom_canvas_prop(self):
        """_summary_
        """
        _file_name = os.path.basename(self.export_file_path)
        self.canvas_obj.setTitle(_file_name)
        self.canvas_obj.setAuthor(USERNAME)

    def populate_pdf(self):

        x_pos, y_pos = self.const.start_x, self.const.start_y
        for video_detail in self.video_details:
            # We will start with setting up the name of the video
            # Set the font
            self.canvas_obj.setFont(self.const.title_font,
                                    self.const.title_size)
            # Set the color
            self.canvas_obj.setFillColor(self.const.title_color)
            # Set the name
            self.canvas_obj.drawString(x_pos, y_pos, video_detail["name"])

            # We only start when 
            if y_pos != self.const.start_y:
                # We have to move the y pos
                y_pos += self.const.titlefactor_y

            # If we have exceed the page height, we will have to create
            # a new page
            if (y_pos > self.height):
                # Move to a new page
                self.canvas_obj.showPage()
                # let's move to the start positions on that page
                x_pos, y_pos = self.const.start_x, self.const.start_y

            # We will start printing the shot's values
            for key, value in video_detail["details"].items():
                # We have to reset the font and the color from
                # previous change
                # We start with Values and then move to Keys
                self.canvas_obj.setFillColor(self.const.value_color)
                self.canvas_obj.setFont(self.const.value_font)
                self.canvas_obj.drawString(x_pos + self.const.linefactor_x,
                                           y_pos, str(value))
                # Let's add in the key items
                self.canvas_obj.setFillColor(self.const.key_color)
                self.canvas_obj.setFont(self.const.value_font)
                self.canvas_obj.drawRightString(x_pos, y_pos,
                                           str(key) + ":")
                # We have to move the y position now
                y_pos += self.const.linefactor_y
                # If we have exceed the page height, we will have to create
                # a new page
                if (y_pos > self.height):
                    # Move to a new page
                    self.canvas_obj.showPage()
                    # let's move to the start positions on that page
                    x_pos, y_pos = self.const.start_x, self.const.start_y

        # Add some custom features
        self._set_custom_canvas_prop()
        # Let's save the canvas object
        self.canvas_obj.save()
