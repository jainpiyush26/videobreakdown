#!/usr/bin/env python
# std imports
from json import tool
import os
import time
import tempfile
import platform
from subprocess import Popen, PIPE

# internal
from .base import get_config, EXPORT_FRAMES, FRAMES_SEL


class VideoFrames(object):
    """_summary_

    Args:
        object (_type_): _description_
    """
    def __init__(self, video_path, video_name, video_framecount,
                 resolution):
        """_summary_

        Args:
            video_path (_type_): _description_
            video_name (_type_): _description_
            video_framecount (_type_): _description_
            aspect (_type_): _description_
            resolution (_type_): _description_
        """
        self.video_path = video_path
        self.name = video_name
        self.video_framecount = video_framecount
        self.resolution = resolution

        self.config = get_config()
        self.framecount = self.config.get("framecount")

    def export_frames(self):
        """_summary_

        Raises:
            RuntimeError: _description_
            RuntimeError: _description_

        Returns:
            _type_: _description_
        """
        _frames = self._get_frames_to_export()

        frames_list = [FRAMES_SEL.format(frame=_frame) for _frame in _frames]
        # Create the frames selection string
        frames_string = "+".join(frames_list)

        # Get the ffmpeg command
        _os = platform.system()
        tool_cmd = self.config.get("tools").get("ffmpeg").get(_os)

        if not os.path.exists(tool_cmd):
            raise RuntimeError("Invalid path for ffmpeg "
                               "command {0}".format(tool_cmd))

        # Create the scale command
        scale = "x".join([str(int(float(item) * self.config.get("factor"))) for
                         item in self.resolution.split("x")])

        # We will be changing the height to -1 to maintain the aspect ratio
        width, _ = scale.split("x")
        updt_scale = "{0}:-1".format(width)

        # Create the output directory
        output_dir = os.path.join(tempfile.gettempdir(),
                                  "{1}_{0}_thmb".format(self.name, time.time()))

        # highly unlikely it exists but
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        # output frames path
        output_frames = os.path.join(output_dir,
                                     "{name}.%04d.jpeg".format(name=self.name))
        export_cmd = EXPORT_FRAMES.format(ffmpeg_cmd=tool_cmd,
                                          input=self.video_path,
                                          scale=updt_scale,
                                          frameselect=frames_string,
                                          output=output_frames)
        # Execute the command
        export_cmd_exec = Popen(export_cmd, stdout=PIPE,
                                stderr=PIPE, shell=True)

        _, std_err = export_cmd_exec.communicate()
        if not str(std_err, encoding="utf-8") == "":
            raise RuntimeError(std_err)

        # return the output directory path
        return output_dir

    def _get_frames_to_export(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        frames = []
        frames_interval = self.video_framecount / (self.framecount - 1)
        for count in range(0, self.video_framecount+1):
            if int(count % frames_interval) == 0:
                frames.append(count)
        frames[-1] = frames[-1]-1
        return frames
