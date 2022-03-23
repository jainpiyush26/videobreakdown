#!/usr/bin/env python
# std imports
import os
from subprocess import Popen, PIPE, call
import platform
import xxhash
import tempfile
import json

# internal import
from .base import get_config, GETTAGS_COMMAND

class VideoInfo(object):
    """_summary_

    Args:
        object (_type_): _description_
    """
    def __init__(self, video_path):
        """_summary_

        Args:
            video_path (_type_): _description_
        """
        self.video_path = video_path
        self._hash_block = 65536
        self.configs = get_config()

    @property
    def hash(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        hex_hash_digest = self._gen_hash()
        return hex_hash_digest

    @property
    def exists(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return os.path.exists(self.video_path)

    @property
    def fileext(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        extension = os.path.splitext(self.video_path)[-1]
        return extension

    @property
    def valid(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        config_data = get_config()
        extension = self.fileext
        # We need this to be lower case (windows oh windows!)
        if extension.lower() in config_data.get("formats"):
            return True
        return False

    @property
    def videoprops(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self._process_video_props()

    @property
    def name(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        base_name = os.path.basename(self.video_path)
        _name = os.path.splitext(base_name)[0]
        return _name

    def _process_video_props(self):
        """_summary_

        Raises:
            RuntimeError: _description_
            RuntimeError: _description_

        Returns:
            _type_: _description_
        """
        property_data = dict()

        # We would also like to add xxhash-64 as one of the items in the
        # dictionary
        property_data["xxhash-64"] = self.hash

        _os = platform.system()
        tools_config = self.configs.get("tools")
        tool_path = tools_config.get("exiftool").get(_os)
        if not tool_path or not os.path.exists(tool_path):
            raise RuntimeError("Invalid EXIFTOOL path {0}".format(tool_path))

        full_tags_dict = self.configs.get("tags")
        tags_dict = full_tags_dict.get("default")

        _ext = self.fileext
        # Let's add any specific tags as per the formats
        if _ext.lower() in full_tags_dict.keys():
            tags_dict.update(full_tags_dict.get(_ext.lower()))

        tags_string = " -".join(tags_dict.keys())
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

        # We are passing only one path per class object so yeah we don't
        # have to check for any other indexes
        for _key, _value in temp_property_data[0].items():
            # We use the more readable keys and ignore not required
            # values (like sourcename)
            if _key not in tags_dict.keys():
                continue
            property_data[tags_dict.get(_key)] = _value.get('val')

        return property_data

    def _gen_hash(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        hasher = xxhash.xxh64()
        with open(self.video_path, "rb") as file_open:
            buffer = file_open.read(self._hash_block)
            while len(buffer) > 0:
                hasher.update(buffer)
                buffer = file_open.read(self._hash_block)
        return hasher.hexdigest()
