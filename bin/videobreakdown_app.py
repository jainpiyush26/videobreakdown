#!/usr/bin/env python
# std imports
import os
import sys
from argparse import ArgumentParser

# Updating system path to get to our files
_python_pck_path = os.path.join(os.path.dirname(__file__), "../", "python")
python_pck_path = os.path.realpath(_python_pck_path)
sys.path.append(python_pck_path)

# internal
from videobreakdown.videoinfo import VideoInfo
from videobreakdown.videoframes import VideoFrames
from videobreakdown.pdfcreator import PdfCreator


def _parse_arguments():
    """_summary_

    Returns:
        _type_: _description_
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
    final_paths = list()
    for _path in os.listdir(dir_path):
        full_path = os.path.join(dir_path, _path)
        if os.path.isdir(full_path):
            final_paths.extend(_process_dirs(full_path))
        else:
            final_paths.append(full_path)
    return final_paths

def main():
    """_summary_
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

    if os.path.exists(pdf_path):
        raise RuntimeError("Path {0} already exists.".format(pdf_path))

    if len(errored_paths):
        raise RuntimeError("Following paths do not exists" 
                           " {0}".format("\n".join(errored_paths)))


    for _path in paths_to_proc:
        print ("Processing - {0}".format(_path))
        video_data = VideoInfo(video_path=_path)
        video_info = video_data.videoprops
        video_name = video_data.name
        print ("Information gathered for {0}".format(video_name))
        print ("Exporting frames...")
        frames_data = VideoFrames(video_path=_path,
                                  video_name=video_name,
                                  video_framecount=video_info.get("Frames"),
                                  resolution=video_info.get("Resolution"))
        # frames_output = frames_data.export_frames()
        # print ("Frames Exporting Finished")
        # frame_paths = [os.path.join(frames_output, frame)
        #                 for frame in os.listdir(frames_output)] 
        frame_paths = []
        frames_info_dict = dict(name=video_name,
                                details=video_info,
                                thumbnails=frame_paths)

        pdf_info_list.append(frames_info_dict)

        print ("="*80)

    print ("Exporting final PDF")
    pdf_creator_object = PdfCreator(video_details=pdf_info_list,
                                    export_file_path=pdf_path)
    pdf_creator_object.populate_pdf()
    print ("PDF Exported to {0}".format(pdf_path))

if __name__ == "__main__":
    main()


