#!python3

# Wishlist:
# Initial release - Deal with multiple streams in A/V content
# Initial release - Handle multiple arguments; handle non-directories
# Initial release - Manage package dependencies
# Initial release - Audio - handle vbr
# Initial release - Handle cson (https://github.com/avakar/pycson)
# Initial release - Handle xml
# Initial release - Parse command line arguments (such as output format)

import os
import sys
import subprocess
import json
import datetime
import fractions
import errno
import distutils.version

import magic # https://github.com/ahupp/python-magic
from PIL import Image # https://pillow.readthedocs.io/
import tabulate

debug = 0
ffprobeExecutable = "ffprobe"


def validateFFProbe():
  # Verify that we have access to ffprobe of the sufficient version.

  minimumFFProbeVersion = "4.1.4" # This is the version I tested against.

  try:
    ffprobeOutput = subprocess.check_output([ffprobeExecutable,"-version"])
  except FileNotFoundError as exceptError:
    if exceptError.errno == errno.ENOENT:
      return(False,"Critical error: ffprobe not found in $PATH.")
    else:
      raise

  ffprobeVersion = str(ffprobeOutput).split(" ")[2]

  try:
    # Compare our version versus baseline.
    if(distutils.version.LooseVersion(ffprobeVersion) >= distutils.version.LooseVersion(minimumFFProbeVersion)):
      return(ffprobeVersion,ffprobeExecutable + " found and is the correct version (" + minimumFFProbeVersion + ") or newer.")
    else:
      return (False,"Critical error: " + ffprobeExecutable + " found, but version " + minimumFFProbeVersion + " or newer required.")
  except Exception as exceptError:
    # This is primarily to account for ffprobe version output formatting potentially changing.
    return(False,"Critical error: unknown critical error in validateFFProbe().\n-->Exception: " + sys.exc_info()[0].__name__ +": " + str(exceptError))


def filterFiles(targetDirectory):
  filteredFileList = list()
  
  unfilteredFileList = os.listdir(targetDirectory)
  
  for file in unfilteredFileList:
    absPathFile = "/".join([targetDirectory,file])
    mimeType = validateFile(absPathFile)
    if(isinstance(mimeType, str)):
      filteredFileList.append([absPathFile, mimeType])

      if(debug):
        print("DEBUG: match: " + ":".join([mimeType,absPathFile]))
      
  return(filteredFileList)


def validateFile(fileName):
  if(os.path.isfile(fileName)):
    mimeType = magic.from_file(fileName,mime=True)
    
    if(debug):
      print("DEBUG: mime category: " + ":".join([mimeType.split("/")[0],fileName]))
    
    if((mimeType.startswith('video/')) or
       (mimeType.startswith('audio/')) or
       (mimeType.startswith('image/'))
      ):
      
      return mimeType

  return False
      

def getFileSizeText(fileSize, suffix='B'):
# from https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    
  for unit in ['','K','M','G','T','P','E','Z']:
    if abs(fileSize) < 1024.0:
      return "%3.1f%s%s" % (fileSize, unit, suffix)

    fileSize /= 1024.0

  fileSizeText = "%.1f%s%s" % (fileSize, 'Y', suffix)

  return fileSizeText


def getAspectRatio(width,height):

  if(height > 0 and width > 0):

    lcn = fractions.Fraction(width,height).numerator
    lcd = fractions.Fraction(width,height).denominator
  
## This code returns "-" if the aspect ratio is the same as the dimensions.
#    if ((not width == lcn) and (not height == lcd)):
#      if(debug >= 2):
#        print("DEBUG: aspect ratio: " + str(lcn) + ":" + str(lcd))
#      return(str(lcn) + ":" + str(lcd))
 
    if(debug >= 2):
      print("DEBUG: Aspect ratio: " + str(lcn) + ":" + str(lcd))

    return(str(lcn) + ":" + str(lcd))

  if(debug >= 2):
    print("DEBUG: No aspect ratio reduction")
    return(None)


def getStreamCount(avsStreams,handlerType):
  streamCounter = 0
  numStreams = 0

  for iterator in avsStreams['streams']:

    if('tags' in iterator):
      if(debug >= 4):
        print("DEBUG: " + json.dumps(iterator['tags'], indent=4))

      if('handler_name' in iterator['tags']):
        if(iterator['tags']['handler_name'] == handlerType):
          numStreams += 1

    streamCounter += 1
    if(debug):
      print("DEBUG: streamCounter: " + str(streamCounter))
  
  if(debug):
    print("DEBUG: avsStreams: " + str(avsStreams))                  
    print("DEBUG: numStreams/" + ": ".join([handlerType,str(numStreams)]))

  return numStreams


def getAVStreamMetadata(avStreamAttributes,avStreamType):
# This routine returns the first matching (and thus likely primary) stream.

  for stream in avStreamAttributes:
    if stream.get('codec_type') == avStreamType:
      return stream
  return False


def getAVFileMetadata(avFile,outputFormat):
  avFileMetadata = dict()
  ffprobeCommandLine = [ffprobeExecutable,"-show_format","-show_streams","-loglevel","quiet","-print_format","json"]
  handler_Audio_text = 'SoundHandler'
  handler_Subtitle_text = 'SubtitleHandler'
  handler_Video_text = 'VideoHandler'
  modeToBpp = {"1": 1, "L": 8, "P": 8, "RGB": 24, "RGBA": 32, "CMYK": 32, "YCbCr": 24, "LAB": 24,
               "HSV": 24, "I": 32, "F": 32, "I;16": 16, "I;16B": 16, "I;16L": 16, "I;16S": 16,
               "I;16BS": 16, "I;16LS": 16, "I;32": 32, "I;32B": 32, "I;32L": 32, "I;32S": 32,
               "I;32BS": 32, "I;32LS": 32} # https://stackoverflow.com/questions/1996577/how-can-i-get-the-depth-of-a-jpg-file


# Universal attributes
  # Populate metadata dictionary
  # JSON-only
  if(outputFormat == 'json'):
    avFileMetadata['fileName'] = avFile[0]
    avFileMetadata['fileSize'] = os.path.getsize(avFile[0])
  # Other format types
  else:
    avFileMetadata['fileName'] = os.path.basename(avFile[0])
    avFileMetadata['fileSize'] = getFileSizeText(os.path.getsize(avFile[0]))
  
  # Applicable to all output formats
  avFileMetadata['mimeType'] = avFile[1]

# Image-specific attributes via Pillow
  if(avFile[1].startswith('image')):
    iAttributes = Image.open(avFile[0])

    # JSON-only
    if(outputFormat == 'json'):
#      avFileMetadata['fileDuration'] = False # TODO: What if it's an MJPEG?
      pass
    else:
#      avFileMetadata['fileDuration'] = '-'
      pass

    # Applicable to all output formats
    if(iAttributes.info['jfif']):
      avFileMetadata['containerFormat'] = 'jfif'
    else:
      avFileMetadata['containerFormat'] = iAttributes.format.lower() # This is not actually the same -i.e. JFIF vs JPEG

#    avFileMetadata['bitRate'] = "-" # TODO: What if it's an MJPEG?
    avFileMetadata['vCodec'] = iAttributes.format.lower()

#    avFileMetadata['fileDuration'] = False # TODO: What if it's an MJPEG?
    avFileMetadata['width'] = int(iAttributes.size[0])
    avFileMetadata['height'] = int(iAttributes.size[1])
    avFileMetadata['aspectRatio'] = getAspectRatio(avFileMetadata['width'],avFileMetadata['height'])
    avFileMetadata['vBitDepth'] = modeToBpp[iAttributes.mode]

#    if(debug > 10):
#      print(iAttributes.info)

  else:
# A/V attributes via ffprobe/ffmpeg
    # Execute ffmpeg, dump output to json
    try:
      ffprobeCommandLine.append(avFile[0])
      ffprobeOutput = subprocess.check_output(ffprobeCommandLine)
    except FileNotFoundError as exceptError:
      if exceptError.errno == errno.ENOENT:
        print("Critical error: " + ffprobeExecutable + " not found in $PATH.")
      else:
        raise

    # Parse json
    avsAttributes = json.loads(ffprobeOutput)
    if(debug > 4):
      print("DEBUG: " + ffprobeExecutable + " output: " + ffprobeOutput.decode('utf8'))

    vAttributes = getAVStreamMetadata(avsAttributes['streams'],'video') # Get metadata of first video stream
    aAttributes = getAVStreamMetadata(avsAttributes['streams'],'audio') # Get metadata of first audio stream

    # JSON-only
    if(outputFormat == 'json'):
      avFileMetadata['fileDuration'] = float(avsAttributes['format'].get('duration'))
    else:
      avFileMetadata['fileDuration'] = str(datetime.timedelta(seconds=int(float(avsAttributes['format'].get('duration')))))
 
    # Applicable to all output formats
    avFileMetadata['containerFormat'] = avsAttributes['format'].get('format_name')
    avFileMetadata['bitRate'] = avsAttributes['format'].get('bit_rate')

    # Get attributes for video streams
    if (vAttributes):
      avFileMetadata['vCodec'] = vAttributes.get('codec_name')
      avFileMetadata['width'] = int(vAttributes.get('width'))
      avFileMetadata['height'] = int(vAttributes.get('height'))
      avFileMetadata['aspectRatio'] = vAttributes.get('display_aspect_ratio')
      avFileMetadata['vFrameRate'] = vAttributes.get('r_frame_rate')
      avFileMetadata['vStreams'] = getStreamCount(avsAttributes,handler_Video_text)

    # Get attributes for audio streams
    if(aAttributes):
      avFileMetadata['aCodec'] = aAttributes.get('codec_name')
      avFileMetadata['aFrequency'] = aAttributes.get('sample_rate')
#      avFileMetadata['aBitRate'] = aAttributes.get('bit_rate')
      avFileMetadata['aChannels'] = aAttributes.get('channels')
      avFileMetadata['aStreams'] = getStreamCount(avsAttributes,handler_Audio_text)
    
    # Get count of subtitles
    avFileMetadata['subtitles'] = getStreamCount(avsAttributes,handler_Subtitle_text)

  return avFileMetadata


def outputTable(avTable,outputFormat):

  if(outputFormat in tabulate.tabulate_formats):
    print(tabulate.tabulate(avTable,tablefmt=outputFormat,headers='keys'))
  else:
    if(outputFormat == 'json'):
      print(json.dumps(avTable,indent=4))
    else:
      return False
  return True


def main():
  outputFormat = 'plain' # Default

  avFileList = list()

  ffprobeValidation = validateFFProbe()
  if (ffprobeValidation[0] == False):
    print(ffprobeValidation[1])
    exit(-1)

  # should become sys.argv[1]
  if len(sys.argv) > 1:
    targetDirectory = os.path.abspath(sys.argv[1]) # TODO: Verify that this directory is accessible
  else:
    targetDirectory = os.getcwd()

  if(debug >= 1):
    print("DEBUG: cwdContents - " + targetDirectory + " " + str(os.listdir(targetDirectory)))

  #for avFile in sys.argv[1:]:
  filteredFiles = filterFiles(targetDirectory)

  if len(filteredFiles) == 0:
    exit(0)

  if(debug):
    print("DEBUG: " + str(filteredFiles))
    
  for avFile in filteredFiles:

    avFileMetadata = getAVFileMetadata(avFile,outputFormat)

    if(debug >= 2):
      print("DEBUG: avFileMetadata: " + str(avFileMetadata))
    
    avFileList.append({
      'filename': avFileMetadata.get('fileName'),
      'size': avFileMetadata.get('fileSize'),
      'time': avFileMetadata.get('fileDuration'),
      'contfmt': avFileMetadata.get('containerFormat'),
      'bitrate': avFileMetadata.get('bitRate'),
      'vcodec': avFileMetadata.get('vCodec'),
      'width': avFileMetadata.get('width'),
      'height': avFileMetadata.get('height'),
      'vframerate': avFileMetadata.get('vFrameRate'),
      'vbitdepth': avFileMetadata.get('vBitDepth'),
      'vstreams': avFileMetadata.get('vStreams'),
      'vratio': avFileMetadata.get('aspectRatio'),
      'acodec': avFileMetadata.get('aCodec'),
      'afreq': avFileMetadata.get('aFrequency'),
      'achans': avFileMetadata.get('aChannels'),
      'astreams': avFileMetadata.get('aStreams'),
#      'alangs': avFileMetdata.get('alangs'),
      'subs': avFileMetadata.get('subtitles'),
#      'slangs': avFileMetdata.get('slangs'),
      'mimetype': avFileMetadata.get('mimeType')
      })

  outputTable(avFileList,outputFormat)

if __name__== "__main__":
    main()
