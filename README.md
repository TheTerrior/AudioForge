# AudioForge
Audio Conversion and Comparison Tool for Linux

Prerequesites:
Python
PySimpleGUIQt (Python Module)
Flac
WavPack
FFmpeg

Documentation:
Allows you to compare two files (simple or advanced), convert from one file to another (within supported formats), and bulk convert.

Compare:
Allows you to choose between simple and advanced. Simple will compare the bits using FFmpeg comparison. Advanced will first convert both files to wav, then compare these two wavs. Both settings will return whether the files are bit-perfect or not. Advanced provides a more accurate output.

Convert:
Allows you to convert from one supported filetype to another. Tags will not be converted, audio only. Allows  you to choose custom directories, and will create new directories if it does not yet exist. You can also choose from a simple drop-down list for express conversion.

Convert+:
This provides the ability for bulk conversion. Input accepts a folder directory instead of file. The program can be specified to only convert files of a certain type, or all files with a supported filetype. They will be converted and outputted to a new folder. The user can also choose to include subdirectories, will be organized exactly like the original folder.

Supported Formats:
wav, wv, flac, aiff

For more detailed error logs from the program, check the command line!
