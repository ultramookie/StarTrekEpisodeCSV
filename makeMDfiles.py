#!/usr/bin/env python
#
# makeMDfiles.py SERIES SEASON CSVFILE

import sys
import csv

# Code for series
# ENT - Enterprise
# TOS - The Original Series
# TAS - The Animated Series
# TNG - The Next Generation
# DS9 - Deep Space Nine
# VOY - Voyager
series = sys.argv[1]
season = '0' + sys.argv[2]
filename = sys.argv[3]

reader = csv.DictReader(open(filename, 'rb'))

for episode in reader:
  episodeNum = episode['num'].zfill(2)
  episodeTitle = episode['title']
  episodeFileTitle = episodeTitle.replace(" ", "-")
  episodeInfo = series + '-S' + season + 'E' + episodeNum + '-' + episodeFileTitle
  episodeFilename = 'YYYY-MM-DD-' + episodeInfo + '.md'
  fileTitle = episodeTitle + ' (' + series + ' S' + season + 'E' + episodeNum + ')' + '\n'
  episodeFile = open(episodeFilename,'w')
  episodeFile.write(fileTitle)
  episodeFile.write('=======================\n')
  episodeFile.write('Month DD, 2016')
  episodeFile.close()