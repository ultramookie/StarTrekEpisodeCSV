#!/usr/bin/env python
#
# makeMDfiles.py INPUTDIR OUTPUTDIR
#
# INPUTDIR = directory with directories of csv files
#
# makeMDfiles.py ~/StarTrekEpisodeCSV/episodes/ /tmp/episodes/
#

import sys
import csv
import glob2
import os

#series = sys.argv[1]
#season = '0' + sys.argv[2] #filename = sys.argv[3]

inputDir = sys.argv[1].rstrip('/')
inputFiles = inputDir + '/**/*.csv'
outputDir = sys.argv[2].rstrip('/')

csvFiles = glob2.glob(inputFiles)

for file in csvFiles:
  pathBreak = file.split('/')
  season = str(pathBreak[-1].split('.')[0]).zfill(2)
  series = pathBreak[-2]

  reader = csv.DictReader(open(file, 'rb'))

  for episode in reader:
    episodeNum = episode['num'].zfill(2)
    episodeTitle = episode['title']
    episodeFileTitle = episodeTitle.replace(" ", "-")
    episodeInfo = series + '-S' + season + 'E' + episodeNum + '-' + episodeFileTitle
    episodeFilename = episodeInfo + '.md'
    fileTitle = episodeTitle + ' (' + series + ' S' + season + 'E' + episodeNum + ')' + '\n'
    directory = outputDir + '/' + series
    if not os.path.exists(directory):
      os.makedirs(directory)
    outputFile = directory + '/' + episodeFilename
    episodeFile = open(outputFile,'w')
    episodeFile.write(fileTitle)
    episodeFile.write('=======================\n')
    episodeFile.close()
