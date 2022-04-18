#!/usr/bin/env python
# std imports
from json import tool
import os
import time
import tempfile
from subprocess import Popen, PIPE
import numpy as np
from PIL import Image, ImageOps

# internal
from .base import get_config, EXPORT_FRAMES, FRAMES_SEL, OS


class VideoFrames(object):
    """ Video frames class object

    Args:
        object (_type_): _description_
    """
    def __init__(self, video_path, video_name, video_framecount,
                 resolution):
        """ Initialization function

        Args:
            video_path (`str`): Path of the video
            video_name (`str`): Name of the video
            video_framecount (`int`): How many frames video has
            aspect (`str`): Aspect ratio of the video
            resolution (`str`): Resolution value of the video
        """
        self.video_path = video_path
        self.name = video_name
        self.video_framecount = video_framecount
        self.resolution = resolution

        self.config = get_config()
        self.framecount = self.config.get("framecount")
        self.scale = "x".join([str(int(float(item) * self.config.get("factor")))
                               for item in self.resolution.split("x")])

    def export_frames(self):
        """ Export frames from the video for the given resolution
            and aspect ratio

        Raises:
            RuntimeError: FFMPEG command does not exist
            RuntimeError: Export command failed

        Returns:
            `str`: directory path of the thumbnails exported
        """
        _frames = self._get_frames_to_export()

        frames_list = [FRAMES_SEL.format(frame=_frame) for _frame in _frames]
        # Create the frames selection string
        frames_string = "+".join(frames_list)

        # Get the ffmpeg command
        tool_cmd = self.config.get("tools").get("ffmpeg").get(OS)

        if not os.path.exists(tool_cmd):
            raise RuntimeError("Invalid path for ffmpeg "
                               "command {0}".format(tool_cmd))

        # We will be changing the height to -1 to maintain the aspect ratio
        width, _ = self.scale.split("x")
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
        # Do hardware acceleration
        _hrdwre_acc = self.config.get("hw_accel", "")

        # Build the export command
        export_cmd = EXPORT_FRAMES.format(ffmpeg_cmd=tool_cmd,
                                          input=self.video_path,
                                          scale=updt_scale,
                                          frameselect=frames_string,
                                          output=output_frames,
                                          hw_accel=_hrdwre_acc)
        print (export_cmd)

        # Execute the command
        export_cmd_exec = Popen(export_cmd, stdout=PIPE,
                                stderr=PIPE, shell=True)

        _, std_err = export_cmd_exec.communicate()
        if not str(std_err, encoding="utf-8") == "":
            raise RuntimeError(std_err)

        # Combination image return
        output_image_comb = os.path.join(
            output_dir, "{name}.combine.jpeg".format(name=self.name))

        self._combine_images(output=output_dir,
                             output_name=output_image_comb)

        # return the output directory path
        return output_image_comb

    def _combine_images(self, output, output_name):
        """ Combine the images into a single thumbnail

        Args:
            output (`str`): Thumbnail output directory
            output_name (`str`): Thumbnail output name
        """
        thumbnail_dirs = os.listdir(output)
        thumbnail_dirs = [os.path.join(output, thmb) for thmb in thumbnail_dirs]
        images = [ Image.open(img) for img in thumbnail_dirs ]
        min_shape = sorted([(np.sum(img.size), img.size) \
            for img in images])[0][1]
        _comb_img = list(np.asarray(img.resize(min_shape)) for img in images)
        images_combination = np.hstack(_comb_img)

        image_combine = Image.fromarray(images_combination)
        # To manage the PDF oddity we are flipping the exported thumbnail
        image_combine = ImageOps.flip(image_combine)
        image_combine.save(output_name)

    def _get_frames_to_export(self):
        """ We will calculate the frames that needs to be exported

        Returns:
            `list`: Frame list that needs to be exported
        """
        frames = []
        if self.video_framecount < self.framecount:
            return range(0, self.video_framecount+1)
        frames_interval = int(self.video_framecount / (self.framecount - 1))
        for count in range(0, self.video_framecount+1):
            if int(count % frames_interval) == 0:
                frames.append(count)
        # Accounting for the floating point round off
        frames[-1] = frames[-1]-1
        return frames
