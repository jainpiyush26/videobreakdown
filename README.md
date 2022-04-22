# VideoBreakdown

The application is a simple open source way to create a detailed informative pdf of your MP4/MOVs files. We extract all the information using the "exiftool" and generate the thumbnails using the "ffmpeg" application. The PDF generated has DETAILS | THUMBNAILS for each video file, all the even entries has a blue background for better readability. 

The details includes -
 - Hash
 - FileSize
 - FileType
 - CreateDate
 - ImageSize
 - CompressorID
 - VideoFrameRate
 - Duration
 - Frames
 - ColorSpace

## Requisites
There are certain python dependencies and 3rd part dependencies are needed. For the 3rd party softwares please keep the paths around, we will need to update the application's config file with that.

### Python Version Dependency
Version needed is: **Python 3.8+**

> **NOTE**: This code has not been tested with Python 2.X versions.

### "pip" install requirements
You can run the following to install all the pip modules
```
pip3 install requirements.txt
```

> **NOTE**: The requirements.txt is part of the git package.

### exiftool
Version needed is: **exiftool-12.40+**

> **NOTE**: For *Windows*, you can download the executable and copy the *exiftool* executable path

> **IMPORTANT**: For *Windows*, you will have to rename the *exiftool(-k).exe* to *exiftool.exe* . This will ensure the exiftool does not wait for an input to close the app.

### ffmpeg
Version needed is: **4.4.1+**

> **NOTE**: For *Windows*, you can download the executable and copy the *ffmpeg* executable path


## Usage
Before we start using the code we have to setup a few things to be able to use the code properly

### Setting up the config.yml

We will copy the **config.yml** to **appconfig.yml**.
```
cp <GIT_LOCATION>/config.yml <GIT_LOCATION>/appconfig.yml
```
You will have to update the following entries in the **appconfig.yml**, the OS's executabe path needs to be updated
- exiftool 
- ffmpeg
```
# Add in the details about the exiftool data per operating system
tools:
  # We want the fully qualified paths and note relative paths
  exiftool:
    # IMPORTANT: For exiftool do not use exiftool(-k).exe, just rename
    # it to ensure it doesn't ask for confirmation on exit during cmd run
    # NOTE: I would recommend using forward slashes for windows paths as well!
    Windows: EXECUTABLE PATH
    Darwin: EXECUTABLE PATH
  ffmpeg:
    # NOTE: use forward slashes for windows paths!
    Windows: EXECUTABLE PATH
    Darwin: EXECUTABLE PATH
```
This will setup the code to run with your machine specific settings

### Updating environment variables

For your OS (windows, mac or linux) you will have to update the following environment variables. If the environment variable does not exists then you can create one.
 - PATH = <GIT_LOCATION>/bin
 - PYTHONPATH = <GIT_LOCATION>/python

## Running the application
Here are the options that are available for the applications 
```
usage: Video Breakdown Code [-h] --path [PATH ...] --export-path EXPORT

optional arguments:
  -h, --help            show this help message and exit
  --path [PATH ...], -p [PATH ...]
                        File(s) or Folder path that contains video files
  --export-path EXPORT, -e EXPORT
                        PDF File that the breakdown information should be exported to.
```
### There are two arguments and they are honestly pretty straight forward
 - Path: This can be either a folder or a single path or multiple paths video paths
 - Export Path: PDF file that you want the PDF export to, it won't overwrite and will throw a runtime error if it already exists

### Modifying the configs
We have a few options that we can change in the config file
- formats : If you want to use this on more video file formats
- framecount : The amount of thumbnails 
- factor : If the exported thumbnails scale needs to be changed
- ***hw_accel : If you do not have a graphics card on your machine, this needs to be commented out***

## Regeneration Help Files
To regenerate the documentations you can run the following from your **<GIT_LOCATION>**
```
pydoc videobreakdown
```
