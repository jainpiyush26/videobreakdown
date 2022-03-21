#!/usr/bin/env python
# std imports
import os
import tempfile
import platform
from subprocess import Popen, PIPE, call

# internal
from base import get_config, EXPORT_FRAMES, FRAMES_SEL


class VideoFrames(object):
    def __init__(self, video_path, video_name, video_framecount, aspect,
                 resolution):
        self.video_path = video_path
        self.name = video_name
        self.video_framecount = video_framecount
        self.aspect = aspect
        self.resolution = resolution

        self.config = get_config()
        self.framecount = self.config.get("framecount")


    def _get_output(self):
        temp_dir_obj = tempfile.TemporaryDirectory(prefix=self.name,
                                                   ignore_cleanup_errors=True)
        return temp_dir_obj

    def export_frames(self):
        _frames = self._get_frames_to_export()
        frames_list = [FRAMES_SEL.format(FRAME=_frame) for _frame in _frames]
        frames_string = "+".join(frames_list)
        _os = platform.system()
        tool_cmd = self.config.get("tools").get("ffmpeg").get(_os)
        scale = "x".join([int(float(item) * self.config.get("factor")) for
                         item in self.resolution.split("x")])
        aspect = self.aspect.replace(":", "/")
        output_dir = _get_output()

        export_cmd = EXPORT_FRAMES.format(ffmpeg_cmd=tool_cmd,
                                          input=self.video_path,
                                          scale=scale, aspect=aspect,
                                          output=)

        output_dir.cleanup()

    def _get_frames_to_export(self):

        frames = []
        frames_interval = self.vidoe_framecounts / (self.framecount - 1)
        for count in range(0, frames + 1):
            if int(count % frames_interval) == 0:
                frames.append(count)
        return frames



