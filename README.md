# avls
avls - Directory listing for audio, images, and video

This is a simple tool which outputs basic metadata about all of the media (audio, images, and video) in a given directory. avls accepts a single optional argument - the directory to scan. If no argument is given, it uses the current working directory.

avls utilizes (and thus requires) ffmpeg to scan audio and video. It utilizes Pillow for image scanning.

It currently outputs table format, but a future iteration will allow you to specify output format at the command line, including JSON, TeX, HTML, etc. using the tabulate library.
