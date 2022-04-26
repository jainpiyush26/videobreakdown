#!/usr/bin/env python
# std imports
import os
from pkgutil import get_data
import re
import sys
import subprocess
from argparse import ArgumentParser

# internal
from videobreakdown.videoinfo import VideoInfo
from videobreakdown.videoframes import VideoFrames
from videobreakdown.pdfcreator import PdfCreator
from videobreakdown.base import OS, get_dimensions, validate_input



def _parse_arguments():
    """Argument parser function

    Returns:
        `Namespace` : Argument parser object
    """
    help_str = "Video Breakdown Code"
    args = ArgumentParser(help_str)
    path_help = "File(s) or Folder path that contains video files"
    args.add_argument("--path", "-p", nargs="*", help=path_help,
                      required=True)
    export_pdf_help = "PDF File that the breakdown information should "\
                      "be exported to."
    args.add_argument("--export-path", "-e", dest="export", required=True,
                      help=export_pdf_help)

    return args.parse_args()


def _process_dirs(dir_path):
    """_summary_

    Args:
        dir_path (`str`): directory path to search the video files from

    Returns:
        `list`: List of file paths for the videos after recursive search
                of the directory entered
    """
    final_paths = list()
    for _path in os.listdir(dir_path):
        full_path = os.path.join(dir_path, _path)
        if os.path.isdir(full_path):
            final_paths.extend(_process_dirs(full_path))
        else:
            final_paths.append(full_path)
    return final_paths

def _open_pdf(pdf_path):
    """ Open the genereated PDF depending on the which OS
    we are on.

    Args:
        pdf_path (`str`): _description_
    """
    if OS == "Darwin": # Mac OS
        subprocess.call(('open', pdf_path))
    elif OS == "Windows": # Windows
        os.startfile(pdf_path)
    else: # Linux
        subprocess.call(('xdg-open', pdf_path))


def main():
    """ Main function that will run the video info, breakdown
        and pdf creation

    Raises:
        RuntimeError: _description_
        RuntimeError: _description_
        RuntimeError: _description_
    """
    arg = _parse_arguments()
    path = arg.path
    pdf_path = arg.export

    errored_paths = list()
    paths_to_proc = list()

    pdf_info_list = list()

    for _path in path:
        # Check if the path exists or not!
        if not os.path.exists(_path):
            errored_paths.append(_path)
            continue
        if os.path.isdir(_path):
            paths_to_proc.extend(_process_dirs(_path))
        else:
            paths_to_proc.append(_path)

    # Lets check if the path provided is directory or not
    if os.path.isdir(pdf_path):
        raise RuntimeError("Path {0} is not a file path!".format(pdf_path))

    # Let's check if the path already exists or not
    if os.path.exists(pdf_path):
        raise RuntimeError("Path {0} already exists.".format(pdf_path))

    # If path does not exists, then let's report that
    if len(errored_paths):
        raise RuntimeError("Following paths do not exists"
                           " {0}".format("\n".join(errored_paths)))

    # store the framepaths
    framepaths = []
    for _path in paths_to_proc:
        print ("Processing - {0}".format(_path))
        if not validate_input(_path):
            print ("WARNING: Cannot process the path, the format does not match"
                   " the allowed formats. SKIPPING")
        # Video Info object will be created for the video path
        video_data = VideoInfo(video_path=_path)
        video_info = video_data.videoprops
        video_name = video_data.name
        print ("Information gathered for {0}".format(video_name))
        print ("Exporting frames...")
        # Let's export the frames
        frames_data = VideoFrames(video_path=_path,
                                  video_name=video_name,
                                  video_framecount=video_info.get("Frames"),
                                  resolution=video_info.get("Resolution"))
        frames_path = frames_data.export_frames()
        framepaths.append(frames_path)
        print ("Frames exporting and combining finished")
        # Store all this in the information
        frames_info_dict = dict(name=video_name,
                                details=video_info,
                                thumbnail=frames_path,
                                scale=frames_data.scale)
        # Insert into the pdf info list
        pdf_info_list.append(frames_info_dict)

        print ("="*80)

    # Let's start creating the PDF creator object
    print ("Exporting final PDF")
    pdf_creator_object = PdfCreator(video_details=pdf_info_list,
                                    export_file_path=pdf_path,
                                    pdf_dimensions=get_dimensions(framepaths))
    pdf_creator_object.populate_pdf()
    print ("PDF Exported to {0}".format(pdf_path))

    print ("Opening the PDF file")
    _open_pdf(pdf_path=pdf_path)

if __name__ == "__main__":
    main()


