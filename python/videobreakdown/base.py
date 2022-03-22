#!/usr/bin/env python
import os
import yaml

SELF_PATH = os.path.realpath(__file__)
SELF_DIR_PATH = os.path.dirname(SELF_PATH)
CONFIG_PATH = os.path.realpath(os.path.join(SELF_DIR_PATH, "../..", "config.yml"))
GETTAGS_COMMAND = '"{toolpath}" -args -T -{tags} {video} -j > {output}'
# Frames export command
EXPORT_FRAMES = "{ffmpeg_cmd} -i {input} " \
                "-vf scale={scale},setdar={aspect},select='{frameselect}' " \
                "-vsync 0 {output} -hide_banner -loglevel error"
FRAMES_SEL = "eq(n\,{frame})"


def get_config():
    """_summary_

    Returns:
        _type_: _description_
    """
    with open(CONFIG_PATH, "r") as file_open:
        config_data = yaml.safe_load(file_open)
    return config_data


