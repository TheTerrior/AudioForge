# AudioForge
Audio Conversion and Comparison Tool for Linux

Prerequesites:
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
This provides the ability for bulk conversion. Input accepts a folder directory instead of file. The input files can be specified to a single filetype, or the input can accept all supported filetypes within the given directory. All input files will be converted to a user-specified filetype. They will be outputted to a new folder.

Supported Formats:
wav, wv, flac, aiff
