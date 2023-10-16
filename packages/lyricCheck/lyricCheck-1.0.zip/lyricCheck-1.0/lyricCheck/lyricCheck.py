#!/usr/bin/env python
#python lyric checker
#Jim Boulter
#January 19, 2015
#Copyright 2015

import sys
import urllib2
import fileinput
from decimal import *
from re import *
from pygoogle import pygoogle

def help():
	print 'usage: python check.py filename.txt\n'
	print 'input line structure: artist name; song title\n'

def lyricCheck(filename):
	elif(str(filename).lower == "help" or str(filename).lower == "-h"):
	help()
	return

	EXPLITIVES = ['fuck', 'shit', 'piss', 'cunt', 'cocksucker', ' tits ']
	inputFile = open(sys.argv[1], 'r')
	queries = list(inputFile)
	outputFile = open(str(sys.argv[1])[:-4] + '_checked.txt', 'w')
	details = '-------------------------\n'

	for track in queries:
		if("\n" in track):
			track = track[:-1]
		print '\nChecking: ' + track
		q = pygoogle(track + ' lyrics')
		q.pages = 1
		urls = q.get_urls()

		checked = len(urls)
		good = 0
		bad = 0
		count = 0

		outputFile.write('[' + track + ']: ')
		details += '[' + track + ']:\n'
		for url in urls:
			if("youtube" in url or "tumblr" in url):
				checked -= 1
				count -= 1
				continue

			actual = False
			song = track[track.find(';')+1:]
			while (len(song) != 0):
				if(song.find(' ') != -1):
					first = song[:song.find(' ')]
					if(first != 'the' and first != 'a' and first != '' and first != ' ' and first in url):
						actual = True
					song = song[song.find(' ')+1:]
					continue
				else:
					if(song in url):
						actual = True
					song = ''


			if(not actual):
				checked -= 1
				count -= 1
				continue
			

			print 'Checking: [' + url + ']'
			details += '    [' + url + ']: '
			u = urllib2.urlopen(url)
			source = u.read()
			u.close()

			clean = True
			for swear in EXPLITIVES:
				if(swear in source):
					bad += 1
					details += 'NOT CLEAN\n'
					clean = False
					break

			if(clean):
				good += 1
				details += 'CLEAN\n'

		if(checked == 0):
			details += '\n'
			outputFile.write('NO INFO\n')
			continue

		perc = 0.0
		print checked
		perc = round(Decimal(good) / Decimal(checked) * 100,2)
		outputFile.write(str(perc) + '% CLEAN\n')

	outputFile.write(details)