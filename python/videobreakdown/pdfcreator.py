#!/usr/bin/env python
# std imports
from distutils.util import change_root
from fileinput import filename
import os
import shutil
from PIL import Image

# third party imports
from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes
from reportlab.lib.units import mm
from reportlab.lib.colors import (darkblue,
                                  gray,
                                  black,
                                  lightblue)

# internal imports
from .base import get_config, PdfConstants, USERNAME


class PdfCreator(object):
    """ PDF Creator object

    :param object: _description_
    :type object: _type_
    """
    def __init__(self, video_details, export_file_path, pdf_dimensions):
        """ Initialization function for the class

        Args:
            video_details (`dict`): Dictionary with video details including
                                    framepaths etc
            export_file_path (`str`): File path to export to
            pdf_dimensions (`list`): PDF dimensions to create
        """
        self.video_details = video_details
        self.export_file_path = export_file_path
        self.const = PdfConstants()
        # Convert to mm instead of pixels
        self.pdf_width = 0
        self.tb_wt = pdf_dimensions[0]
        self.tb_ht = pdf_dimensions[1]
        self.config = get_config()
        self.width, self.height = 0, 0
        self.canvas_obj = None


    def _create_canvas(self):
        """ Create the canvas object using the size values
            from arguments and thumbnails

        Raises:
            RuntimeError: PDF Size format cannot be retrieved
            RuntimeError: PDF path already exists
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
                _, self.height = _size_tuple[1], _size_tuple[0]
            else:
                _, self.height = _size_tuple[0], _size_tuple[1]
        elif isinstance(pdf_size, list):
            _, self.height = pdf_size[0], pdf_size[1]
        else:
            raise RuntimeError("Invalid pdf size format"
                               " {0}".format(pdf_size))

        # We check to ensure the PDF path does not already exists, we do not
        # want to overwrite it.
        if os.path.exists(self.export_file_path):
            raise RuntimeError("PDF path {0} already"
                               " exists!".format(self.export_path))

        _len_details = len(self.video_details[0].get("details"))
        _chng_fctr = (_len_details * self.const.linefactor_y)/self.tb_ht

        self.pdf_width = self.tb_wt * _chng_fctr + \
            self.const.thumbnail_x_pos + self.const.width_buffer


        self.canvas_obj = canvas.Canvas(filename=self.export_file_path,
                                        pagesize=(self.pdf_width, self.height),
                                        bottomup=0)


    def _set_custom_canvas_prop(self):
        """ Adding some custom canvas properties
        """
        _file_name = os.path.basename(self.export_file_path)
        self.canvas_obj.setTitle(_file_name)
        self.canvas_obj.setAuthor(USERNAME)

    def _cleanup_temp_files(self):
        """ Clean the temporary files that were created in the
            process (mainly thumbnails and combined thumbnails)
        """
        for video_detail in self.video_details:
            thumnail_path = video_detail.get("thumbnail")
            shutil.rmtree(os.path.dirname(thumnail_path))

    def _populate_pdf(self):
        """ Using the canvas object and the video details
            start filling in the information about the video
            and add the thumbnails
        """
        x_pos, y_pos = self.const.start_x, self.const.start_y
        for video_counter, video_detail in enumerate(self.video_details):

            # We check if we are exceeding the height limits and
            # should we change the page
            expected_end_y_pos = y_pos + self.const.titlefactor_y + \
                                 len(video_detail["details"])*self.const.linefactor_y + \
                                 self.const.linefactor_y

            if (expected_end_y_pos > self.height):
                    # Move to a new page
                    self.canvas_obj.showPage()
                    # let's move to the start positions on that page
                    x_pos, y_pos = self.const.start_x, self.const.start_y
                    expected_end_y_pos = y_pos + self.const.titlefactor_y + \
                                 len(video_detail["details"])*self.const.linefactor_y + \
                                 self.const.linefactor_y

            # For every even entry we want to hightlight with blue
            if video_counter % 2 == 1:
                # Calculating the size (height) of the highlighted section
                hlght_size = expected_end_y_pos - y_pos
                # Add in the highlight rectangle
                self.canvas_obj.setFillColor(self.const.bbox_color)
                self.canvas_obj.rect(0,y_pos-self.const.bbox_overflow,
                                     self.pdf_width, hlght_size, 0, 1)

            # We will start with setting up the name of the video
            # Set the font
            self.canvas_obj.setFont(self.const.title_font,
                                    self.const.title_size)
            # Set the color
            self.canvas_obj.setFillColor(self.const.title_color)
            # Set the name
            self.canvas_obj.drawString(x_pos, y_pos, video_detail["name"])

            # We have to move the y pos
            y_pos += self.const.titlefactor_y

            # We will start adding the images just after the title
            # so this is the thumbnails y value
            thumb_y_pos = y_pos - self.const.linefactor_y
            thumb_x_pos = self.const.thumbnail_x_pos
            _thumbnails = video_detail.get("thumbnail")
            _img = Image.open(_thumbnails)
            _width = _img.width
            _height = (len(video_detail["details"])*self.const.linefactor_y)

            if _thumbnails:
                self.canvas_obj.drawImage(_thumbnails, thumb_x_pos,
                                          thumb_y_pos, width=_width,
                                          height=_height,
                                          preserveAspectRatio=True,
                                          showBoundary=True,
                                          anchor='sw')

            # We will start printing the shot's values
            for key, value in video_detail["details"].items():
                # We have to reset the font and the color from
                # previous change
                # We start with Values and then move to Keys
                self.canvas_obj.setFillColor(self.const.value_color)
                self.canvas_obj.setFont(self.const.value_font,
                                        self.const.text_size)
                self.canvas_obj.drawString(x_pos + self.const.linefactor_x,
                                           y_pos, str(value))
                # Let's add in the key items
                self.canvas_obj.setFillColor(self.const.key_color)
                self.canvas_obj.setFont(self.const.value_font,
                                        self.const.text_size)
                self.canvas_obj.drawRightString(x_pos, y_pos,
                                           str(key) + ":")
                # We have to move the y position now
                y_pos += self.const.linefactor_y

            # Move the position, making it ready for the new entry
            y_pos += self.const.linefactor_y

        # Add some custom features
        self._set_custom_canvas_prop()
        # Let's save the canvas object
        self.canvas_obj.save()

    def populate_pdf(self):
        """ Populate the PDF values
        """
        # Create the canvas object
        self._create_canvas()
        # Populate the pdf file
        self._populate_pdf()
        # Cleanup the temporary files
        self._cleanup_temp_files()
