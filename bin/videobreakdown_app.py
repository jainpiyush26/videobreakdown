#!/usr/bin/env python
# std imports
import os
import time
import subprocess
from argparse import ArgumentParser
import warnings

# internal
from videobreakdown.videoinfo import VideoInfo
from videobreakdown.videoframes import VideoFrames
from videobreakdown.pdfcreator import PdfCreator
from videobreakdown.base import (OS, get_dimensions,
                                 validate_input, uptodate_app_config)



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
                      "be exported to. If left empty, the folder path "\
                      "will be used. Name will be current time stamp."
    args.add_argument("--export-path", "-e", dest="export",
                      help=export_pdf_help)

    return args.parse_args()

def _process_dirs(dir_path):
    """ Process directories

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
    # First thing we check is does the app config matches or not!
    if not uptodate_app_config():
        print("WARNING: You need to make sure the appconfig.yml " \
              "entries match the entries in the " \
              "config.yml, please update with " \
              "the necesssary changes.")
        return
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

    # If we have the PDF path value
    if pdf_path:
        # Lets check if the path provided is directory or not
        if os.path.isdir(pdf_path):
            raise RuntimeError("Path {0} is not a" \
                               " file path!".format(pdf_path))

        # Let's check if the path already exists or not
        if os.path.exists(pdf_path):
            raise RuntimeError("Path {0} already exists.".format(pdf_path))

    else:
        # If the pdf path argument is empty
        current_date = time.strftime("%Y%m%d_%H%M%S_vb.pdf")
        # NOTE: WE TAKE THE FIRST ELEMENT OF THE PATH LIST
        if os.path.isdir(path[0]):
            pdf_path = os.path.join(path[0], current_date)
        else:
            path_dir = os.path.dirname(path[0])
            pdf_path = os.path.join(path_dir, current_date)

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
                   " the allowed formats. SKIPPING...\n\n")
            continue
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
                                  resolution=video_info.get("Resolution"),
                                  video_rotation=video_data.videorotation)

        frames_path = frames_data.export_frames()
        framepaths.append(frames_path)
        print ("Frames exporting and combining finished")
        # Store all this in the information
        vertical = False if video_data.videorotation==0 else True
        frames_info_dict = dict(name=video_name,
                                details=video_info,
                                thumbnail=frames_path,
                                scale=frames_data.scale,
                                vertical=vertical)
        # Insert into the pdf info list
        pdf_info_list.append(frames_info_dict)

        print ("="*80)

    if len(pdf_info_list) == 0:
        print ("Noting to export! Exiting the app.")
        return

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


