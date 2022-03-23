#!/usr/bin/env python
# std imports
import os
import sys

# Updating system path to get to our files
_python_pck_path = os.path.join(os.path.dirname(__file__), "../", "python")
python_pck_path = os.path.realpath(_python_pck_path)
sys.path.append(python_pck_path)

# internal
from videobreakdown.videoinfo import VideoInfo
from videobreakdown.videoframes import VideoFrames


path = video_path=r"D:\work\python_dev\videobreakdown\extras\sample_videos\20220217_DOC_2785.MP4"
data = VideoInfo(video_path=path)
info = data.videoprops

frames_obj = VideoFrames(video_path=path,
                         video_name=data.name,
                         aspect=info.get("AspectRatio"),
                         video_framecount=info.get("Frames"),
                         resolution=info.get("Resolution"))
frames_output = frames_obj.export_frames()


