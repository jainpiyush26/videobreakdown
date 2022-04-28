#!/usr/bin/env python
from asyncio import constants
import os
from numpy import maximum
import yaml
import getpass
import platform
from PIL import Image

# Third party imports
from reportlab.lib.units import mm
from reportlab.lib.colors import (darkblue,
                                  gray,
                                  black,
                                  lightblue)

# Global variables
SELF_PATH = os.path.realpath(__file__)
SELF_DIR_PATH = os.path.dirname(SELF_PATH)
# Config path to be used in the applications
APP_CONFIG_PATH = os.path.realpath(os.path.join(SELF_DIR_PATH, "../..", "appconfig.yml"))
CONFIG_PATH = os.path.realpath(os.path.join(SELF_DIR_PATH, "../..", "config.yml"))
# What tags are to be used
GETTAGS_COMMAND = '"{toolpath}" -api largefilesupport=1 -args -T -{tags} "{video}" -j > \"{output}\"'
# Frames export command
EXPORT_FRAMES = "\"{ffmpeg_cmd}\" {hw_accel} -i \"{input}\" " \
                "-crf 0 -vf {transpose}scale={scale},select='{frameselect}' " \
                "-vsync 0 \"{output}\" -hide_banner -loglevel error"
# Frames selection argument
FRAMES_SEL = "eq(n\,{frame})"

# Get the username
USERNAME = getpass.getuser()

# Operating system
OS = platform.system()

_CONFIG_DICT = dict()

def _get_config():
    """ Read the YAML config for the application

    Returns:
        `dict`: Configuration details and data that will be used in the code
    """
    with open(APP_CONFIG_PATH, "r") as file_open:
        config_data = yaml.safe_load(file_open)
    return config_data

def get_config():
    """ Wrapper function around _get_config to get a singleton object

    Returns:
        `dict`: Configuration dictionary
    """
    global _CONFIG_DICT

    if not _CONFIG_DICT:
        _CONFIG_DICT = _get_config()
    else:
        print ("Calling the dict")

    return _CONFIG_DICT

def uptodate_app_config():
    """ Check if the appconfig.yml version matches to the version entry in
        config.yml

    Returns:
        `bool`: True if the version string matches else False
    """
    app_config_version = get_config().get("version", "v0.0.0")
    with open(CONFIG_PATH, "r") as file_open:
        config_data = yaml.safe_load(file_open)
    config_version = config_data.get("version")
    if app_config_version != config_version:
        return False
    return True

def validate_input(input_path):
    """ Confirm if we can indeed process the path

    Args:
        input_path (`str`): video path
    Returns:
        `bool`: If the extention does not match the config, then it's invalid
    """
    valid_formats = get_config().get("formats")
    path_ext = os.path.splitext(input_path)[-1]
    if path_ext:
        if path_ext.lower() in valid_formats:
            return True

    return False

def get_dimensions(thumbnails):
    """ Get the maximum height and maximum width of
        the thumbnail paths from the list

    Args:
        thumbnails (`list`): list of thumbnail paths

    Returns:
        `int`, `int`: maximum width and maximum height
    """
    maximum_width = 0
    maximum_height = 0
    for _thumbnail in thumbnails:
        _img = Image.open(_thumbnail)
        _width = _img.width
        _height = _img.height
        if _width > maximum_width:
            maximum_width = _width
        if _height > maximum_height:
            maximum_height = _height

    return maximum_width , maximum_height


class PdfConstants(object):
    """ Constant object for the pdf, includes a bunch
        of spaces, buffers and values
    """
    @property
    def start_x(self):
        """ PDF start x position

        Returns:
            `int`: x position value
        """
        return 25 * mm

    @property
    def start_y(self):
        """ PDF start y position

        Returns:
            `int`: y position value
        """
        return 10 * mm

    @property
    def linefactor_x(self):
        """ PDF line x position

        Returns:
            `int`: line x position value
        """
        return 1.5 * mm

    @property
    def linefactor_y(self):
        """ PDF line y position

        Returns:
            `int`: line y position value
        """
        return 5 * mm

    @property
    def titlefactor_x(self):
        """ PDF title x position

        Returns:
            `int`: title x position value
        """
        return 0

    @property
    def titlefactor_y(self):
        """ PDF title y position

        Returns:
            `int`: title y position value
        """
        return 6 * mm

    @property
    def title_size(self):
        """ PDF title font size value

        Returns:
            `int`: title font size value
        """
        return 12

    @property
    def text_size(self):
        """ PDF text font size value

        Returns:
            `int`: pdf text font size value
        """
        return 10

    @property
    def title_color(self):
        """ PDF title color value

        Returns:
            `str`: Color value for the title
        """
        return darkblue

    @property
    def key_color(self):
        """ PDF details key color value

        Returns:
            `str`: Color value for the details key
        """
        return black

    @property
    def value_color(self):
        """ PDF details value color

        Returns:
            `str`: Color value of the details
        """
        return gray

    @property
    def bbox_color(self):
        """ Bounding box color for even entries in the pdf

        Returns:
            `str`: Color value of the bounding box
        """
        return lightblue

    @property
    def key_font(self):
        """ Font value of the details key in the pdf

        Returns:
            `str`: Font name of the details key
        """
        # you can use the function canvas.getAvailableFonts
        # for more options!
        return "Helvetica-Bold"

    @property
    def title_font(self):
        """ Font value of the title in the pdf

        Returns:
            `str`: Font value of the title
        """
        return "Courier-BoldOblique"

    @property
    def value_font(self):
        """ Font value of the details in the pdf

        Returns:
            `str`: Font value of the detail entries
        """
        return "Helvetica"

    @property
    def bbox_overflow(self):
        """ Top and bottom overflow value of the bbox
            around the even entries in the PDF

        Returns:
            `int`: Overflow value
        """
        return 6 * mm

    @property
    def thumbnail_x_pos(self):
        """ Thumbnail x position in the PDF

        Returns:
            `int`: Position where thumbnail will start
        """
        return 70 * mm

    @property
    def width_buffer(self):
        """ Width buffer value to be added after thumbnail entries

        Returns:
            `int`: Buffer value to be added after thumbnails
        """
        return 10*mm
