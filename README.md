# avls
avls - Directory listing for audio, images, and video

This is a simple tool which outputs basic metadata about all of the media (audio, images, and video) in a given directory. avls accepts a single optional argument - the directory to scan. If no argument is given, it uses the current working directory.

avls utilizes (and thus requires) ffmpeg to scan audio and video. It utilizes Pillow for image scanning.

It currently outputs table format, but a future iteration will allow you to specify output format at the command line, including JSON, TeX, HTML, etc. using the tabulate library.

[Requirements](https://github.com/cobaltjacket/avls/blob/master/requirements.txt):

* [Pillow](https://github.com/python-pillow/Pillow)
* [python-magic](https://github.com/ahupp/python-magic)
* [tabulate](https://pypi.org/project/tabulate/)

Sample output:

```
% avls
filename                             size     time     contfmt                    bitrate  vcodec      width    height  vframerate      vbitdepth    vstreams  vratio    acodec       afreq    achans    astreams    subs  mimetype
World At War - S01E19.m4v            967.8MB  0:54:42  mov,mp4,m4a,3gp,3g2,mj2    2473478  hevc         1280       720  24000/1001                          1  16:9      aac          48000         2           1       2  video/mp4
Sultans of Swing.mp3                 8.4MB    0:05:46  mp3                         202280                                                                                mp3          44100         2           0       0  audio/mpeg
magnum-pi-theme-song.mp3             922.4KB  0:00:59  mp3                         127999                                                                                mp3          44100         2           0       0  audio/mpeg
Holy Grail.m4a                       2.1MB    0:02:18  mov,mp4,m4a,3gp,3g2,mj2     127093                                                                                aac          44100         2           1       0  video/mp4
SampleAudioSource.ulaw.wav           2.6MB    0:05:37  wav                          64001                                                                                pcm_mulaw     8000         1           0       0  audio/x-wav
IMG_0097.JPG                         3.0MB             jfif                                jpeg         2448      3264                         24              3:4                                                         image/jpeg
IMG_0093.JPG                         3.3MB             jfif                                jpeg         2448      3264                         24              3:4                                                         image/jpeg
Dead Or Alive - Brand New Lover.mkv  20.2MB   0:03:33  matroska,webm               791613  h264          640       480  25/1                                0  4:3       opus         48000         2           0       0  video/x-matroska
```
