#!/usr/bin/env python
# std imports
import os
from subprocess import Popen, PIPE, call

# internal
from base import get_config


class VideoFrames(object):
    def __init__(self, video_path, video_framecount, aspect, resolution):
        self.video_path = video_path
        self.video_framecount = video_framecount
        self.aspect = aspect
        self.resolution = resolution

        self.config = get_config()
        self.framecount = self.config.get("framecount")

    def _get_frames_to_export(self):

        frames_we_want = []
        frames_interval = self.vidoe_framecounts / (self.framecount - 1)
        for count in range(0, frames + 1):
            if int(count % frames_interval) == 0:
                frames_we_want.append(count)
        return frames_we_want



