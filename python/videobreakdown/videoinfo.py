#!/usr/bin/env python
# std imports
import os
import re
from subprocess import Popen, PIPE, call
from numpy import full
import xxhash
import tempfile
import json
from datetime import datetime

# internal import
from .base import get_config, GETTAGS_COMMAND, OS

class VideoInfo(object):
    """ Video Info class object

    Args:
        object (_type_): _description_
    """
    def __init__(self, video_path):
        """ Initialization function for the class

        Args:
            video_path (`str`): Video path value
        """
        self.video_path = video_path
        self._hash_block = 65536
        self.configs = get_config()
        self._videorotation = 0

    @property
    def hash(self):
        """ Hash value of the video

        Returns:
            `str`: Hash value of the file
        """
        hex_hash_digest = self._gen_hash()
        return hex_hash_digest

    @property
    def exists(self):
        """ Does the video path exists

        Returns:
            `bool`: Does the video path exists or not
        """
        return os.path.exists(self.video_path)

    @property
    def fileext(self):
        """ File extension of the video path

        Returns:
            `str`: File extension of the video
        """
        extension = os.path.splitext(self.video_path)[-1]
        return extension

    @property
    def valid(self):
        """ Is the video of valif format or not

        Returns:
            `bool`: True or False
        """
        config_data = get_config()
        extension = self.fileext
        # We need this to be lower case (windows oh windows!)
        if extension.lower() in config_data.get("formats"):
            return True
        return False

    @property
    def videoprops(self):
        """ Return the video properties, which includes getting
            a bunch of metadata from the video file

        Returns:
            `dict`: Property dict values
        """
        return self._process_video_props()

    @property
    def videorotation(self):
        """ Video rotation property

        Returns:
            `int`: video rotation values
        """
        return self._videorotation

    @videorotation.setter
    def videorotation(self, value):
        """ Sets the video rotation value

        Args:
            value (`int`): Rotation value of the video

        Returns:
            `int`: Rotation value
        """
        self._videorotation = value

    @property
    def name(self):
        """ Name of the video file

        Returns:
            `str`: Video name without the extension
        """
        base_name = os.path.basename(self.video_path)
        _name = os.path.splitext(base_name)[0]
        return _name

    def _get_frames(self, time_duration, fps):
        """ This returns the total number of frames by
            calculating time_duration multiplied by fps


        Args:
            time_duration (`str`): String representation of string
            fps (`int`): fps value of the video

        Returns:
            `int`: Total frames in the video
        """
        # We need to create a time object to calculate the frames
        time_obj = None
        if ":" in time_duration:
            time_obj = datetime.strptime(time_duration, "%H:%M:%S")
        else:
            time_obj = datetime.strptime(time_duration, "%S.%f s")

        total_seconds = (time_obj.hour * 3600) + (time_obj.minute * 60) \
                        + (time_obj.second) + (time_obj.microsecond/1000000)
        total_frames = int(total_seconds * fps)

        return total_frames

    def _process_video_props(self):
        """ Process video properties

        Raises:
            RuntimeError: _description_
            RuntimeError: _description_

        Returns:
            `dict`: Dictionary values including the properties of the video
        """
        property_data = dict()

        # We would also like to add xxhash-64 as one of the items in the
        # dictionary
        property_data["xxhash-64"] = self.hash

        tools_config = self.configs.get("tools")
        tool_path = tools_config.get("exiftool").get(OS)
        if not tool_path or not os.path.exists(tool_path):
            raise RuntimeError("Invalid EXIFTOOL path {0}".format(tool_path))

        full_tags_dict = self.configs.get("tags")
        tags_dict = full_tags_dict.get("default")
        calculated_dict = full_tags_dict.get("calculated")
        misc_dict = full_tags_dict.get("misc")

        # Get the camera type
        camera_list = full_tags_dict.get("camera_model")

        # color tags values
        color_tags_dict = full_tags_dict.get("camera_specific")
        color_tags = []
        for _key, _value in color_tags_dict.items():
            color_tags.append(_value)

        _ext = self.fileext
        # Let's add any specific tags as per the formats
        if _ext.lower() in full_tags_dict.keys():
            tags_dict.update(full_tags_dict.get(_ext.lower()))

        tags_string = " -".join(tags_dict.keys())
        tags_string = tags_string + " -" + " -".join(camera_list)
        tags_string = tags_string + " -" + " -".join(color_tags)
        tags_string = tags_string + " -" + " -".join(misc_dict.keys())

        output_file = tempfile.NamedTemporaryFile(delete=False)
        output_file.close()
        command = GETTAGS_COMMAND.format(toolpath=tool_path,
                                         tags=tags_string,
                                         video=self.video_path,
                                         output=output_file.name)

        command_exec = Popen(command, shell=True, stderr=PIPE, stdout=PIPE)

        _, std_err = command_exec.communicate()

        if command_exec.returncode != 0:
            raise RuntimeError(std_err)

        with open(output_file.name, 'rb') as file_open:
            temp_property_data = json.load(file_open)

        # We have to remove the created temp file once we have read
        # it and created the json dict
        os.remove(output_file.name)

        # We look at the ways we can get the camera model makes from
        # the metadata tags for MAKE or MAJOR MANIFACTURER
        camera_type = None
        camera_model_values = []
        for _tag in camera_list:
            tag_value = temp_property_data[0].get(_tag)
            if tag_value.get('val') != "-":
                camera_model_values.append(tag_value.get('val'))

        # Get the metadata tags for getting the color values
        for _camera_name in color_tags_dict.keys():
            for _model in camera_model_values:
                if re.match(_camera_name, _model, re.I):
                    camera_type = _camera_name
                    break

        # We are passing only one path per class object so yeah we don't
        # have to check for any other indexes
        for _key, _value in temp_property_data[0].items():
            # We use the more readable keys and ignore not required
            # values (like sourcename)
            if _key not in tags_dict.keys() \
                and _key not in misc_dict.keys():
                continue

            if _key in misc_dict.keys():
                if _key == "Rotation":
                    self.videorotation = _value.get('val')
            else:
                keyvalue = _value.get('val')
                keyname = tags_dict.get(_key)
                property_data[keyname] = keyvalue

        # We need to get the calculated values
        for key, values in calculated_dict.items():
            # NOTE: This will have to be updated to get the correct
            # logic for any new calculated value!
            if key == "Frames":
                property_data[key] = self._get_frames(
                    *[property_data.get(_val) for _val in values])

        colorspace_tag = color_tags_dict.get(camera_type)
        colorspace_val = temp_property_data[0].get(colorspace_tag, " - ")
        if colorspace_val != " - ":
            colorspace_val = colorspace_val.get('val')
        property_data["Colorspace"] = colorspace_val

        return property_data

    def _gen_hash(self):
        """ Get the hash value of the vidoe

        Returns:
            `str`: Generate the has of the video
        """
        hasher = xxhash.xxh64()
        with open(self.video_path, "rb") as file_open:
            buffer = file_open.read(self._hash_block)
            while len(buffer) > 0:
                hasher.update(buffer)
                buffer = file_open.read(self._hash_block)
        return hasher.hexdigest()
