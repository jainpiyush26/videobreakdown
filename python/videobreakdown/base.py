#!/usr/bin/env python
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

SELF_PATH = os.path.realpath(__file__)
SELF_DIR_PATH = os.path.dirname(SELF_PATH)
CONFIG_PATH = os.path.realpath(os.path.join(SELF_DIR_PATH, "../..", "config.yml"))
GETTAGS_COMMAND = '"{toolpath}" -args -T -{tags} "{video}" -j > \"{output}\"'
# Frames export command
EXPORT_FRAMES = "{ffmpeg_cmd} -i \"{input}\" " \
                "-crf 0 -vf scale={scale},select='{frameselect}' " \
                "-vsync 0 \"{output}\" -hide_banner -loglevel error"
FRAMES_SEL = "eq(n\,{frame})"

USERNAME = getpass.getuser()

OS = platform.system()

def get_config():
    """_summary_

    Returns:
        _type_: _description_
    """
    with open(CONFIG_PATH, "r") as file_open:
        config_data = yaml.safe_load(file_open)
    return config_data


def get_width(thumbnails):
    maximum_size = 0
    for _thumbnail in thumbnails:
        _img = Image.open(_thumbnail)
        _width = _img.width
        if _width > maximum_size:
            maximum_size = _width
    return maximum_size


class PdfConstants(object):
    """_summary_

    Args:
        object (_type_): _description_

    Returns:
        _type_: _description_
    """
    @property
    def start_x(self):
        return 25 * mm

    @property
    def start_y(self):
        return 10 * mm

    @property
    def linefactor_x(self):
        return 1.5 * mm

    @property
    def linefactor_y(self):
        return 5 * mm

    @property
    def titlefactor_x(self):
        return 0

    @property
    def titlefactor_y(self):
        return 6 * mm

    @property
    def title_size(self):
        return 12

    @property
    def text_size(self):
        return 10

    @property
    def title_color(self):
        return darkblue

    @property
    def key_color(self):
        return black

    @property
    def value_color(self):
        return gray

    @property
    def bbox_color(self):
        return lightblue

    @property
    def key_font(self):

        # you can use the function canvas.getAvailableFonts
        # for more options!
        return "Helvetica-Bold"

    @property
    def title_font(self):
        return "Courier-BoldOblique"

    @property
    def value_font(self):
        return "Helvetica"

    @property
    def bbox_overflow(self):
        return 6 * mm

    @property
    def thumbnail_x_pos(self):
        return 70 * mm

