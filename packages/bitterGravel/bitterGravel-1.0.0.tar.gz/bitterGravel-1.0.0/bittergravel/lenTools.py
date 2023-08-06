#!/usr/bin/env python
###############################################################################
#                                                                             #
#    lenTools.py                                                              #
#                                                                             #
#    Classes for making pretty pctures of contig/read length distributions    #
#                                                                             #
#    Copyright (C) Michael Imelfort                                           #
#                                                                             #
###############################################################################
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program. If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

__author__ = "Michael Imelfort"
__copyright__ = "Copyright 2014"
__credits__ = ["Michael Imelfort"]
__license__ = "GPLv3"
__maintainer__ = "Michael Imelfort"
__email__ = "mike@mikeimelfort.com"

###############################################################################
###############################################################################
###############################################################################
###############################################################################

# system includes
import sys
import mimetypes
import gzip
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d, Axes3D
from pylab import plot,subplot,axis,stem,show,figure
import matplotlib.patches as mpatches

# local includes
from mikeplotlib.cbCols import Cb2Cols as CB2

###############################################################################
###############################################################################
###############################################################################
###############################################################################

class ContigParser:
    """Main class for reading in and parsing contigs"""
    def __init__(self): pass

    def readfq(self, fp): # this is a generator function
        last = None # this is a buffer keeping the last unprocessed line
        while True: # mimic closure; is it a bad idea?
            if not last: # the first record or a record following a fastq
                for l in fp: # search for the start of the next record
                    if l[0] in '>@': # fasta/q header line
                        last = l[:-1] # save this line
                        break
            if not last: break
            name, seqs, last = last[1:].partition(" ")[0], [], None
            for l in fp: # read the sequence
                if l[0] in '@+>':
                    last = l[:-1]
                    break
                seqs.append(l[:-1])
            if not last or last[0] != '+': # this is a fasta record
                yield name, ''.join(seqs), None # yield a fasta record
                if not last: break
            else: # this is a fastq record
                seq, leng, seqs = ''.join(seqs), 0, []
                for l in fp: # read the quality
                    seqs.append(l[:-1])
                    leng += len(l) - 1
                    if leng >= len(seq): # have read enough quality
                        last = None
                        yield name, seq, ''.join(seqs); # yield a fastq record
                        break
                if last: # reach EOF before reading enough quality
                    yield name, seq, None # yield a fasta record instead
                    break

###############################################################################
###############################################################################
###############################################################################
###############################################################################

class FileStats(object):
    '''Storage class for holding info about one file'''
    def __init__(self):
        self.lengthCounts = {}
        self.totalLength = 0

    def addLen(self, l):
        '''Add an observed length to this file's stats

        Inputs:
         l - int, the length to add

        Outputs:
         None
        '''
        try:
            self.lengthCounts[l] += 1
        except KeyError:
            self.lengthCounts[l] = 1
        self.totalLength += l

    def getDistInfo(self):
        '''Transform the hash into an array suitable for plotting etc

        Inputs:
         None

        Outputs:
         None
        '''
        points = []
        for l in range(min(self.lengthCounts.keys()),
                       max(self.lengthCounts.keys())):
            try:
                points.append([l, self.lengthCounts[l]])
            except KeyError:
                points.append([l, 0])
        return np.array(points)

    def __str__(self):
        '''Override print functions'''
        return "\n".join(["%d\t%d" % (l,c) for [l,c] in self.getDistInfo()])

###############################################################################
###############################################################################
###############################################################################
###############################################################################

class LenStatMaker():
    '''Main wrapper for working out len stats for multiple files'''
    def __init__(self):
        self.groupNum = 0
        self.fileStats = {}
        self.file2Groups = {}

    def parseAllFiles(self, fileGroups, subSample=0):
        '''Loop through and parse each of the input files

        Inputs:
         fileGroups - [string, string, ...], grouped paths to files to parse
         subSample - int, only process this many reads (0 for all)

        Outputs:
         None
        '''

        # arrange the filenames into groups
        # groups are used mainly for coloring
        file_names = []
        for group in fileGroups:
            fns = group.split(",")
            for fn in fns:
                self.file2Groups[fn] = self.groupNum
                file_names.append(fn)
            self.groupNum += 1

        # now parse the files
        for file_name in file_names:
            self.fileStats[file_name] = FileStats()
            LSM_open = open
            try:
                # handle gzipped files
                mime = mimetypes.guess_type(file_name)
                if mime[1] == 'gzip':
                    LSM_open = gzip.open
            except:
                print "Error when guessing seq file mimetype for file %s" % \
                    file_name
                raise
            try:
                with LSM_open(file_name, "r") as fh:
                    self.parseOneFile(fh, self.fileStats[file_name], subSample)
            except:
                print "Error opening file:", file_name, sys.exc_info()[0]
                raise

            print file_name, self.fileStats[file_name].totalLength

    def parseOneFile(self, fileHandle, fileStats, subSample=0):
        '''parse one contig or reads file

        Inputs:
         fileHandle - <FILE>, an open contig or reads file
         fileStats - FileStats, a FileStats instance
         subSample - int, only process this many reads (0 for all)

        Outputs:
         None
        '''
        CP = ContigParser()
        if subSample != 0:
            processed = 0
            for name, seq, qual in CP.readfq(fileHandle):
                fileStats.addLen(len(seq))
                processed += 1
                if processed > subSample:
                    break
        else:
            for name, seq, qual in CP.readfq(fileHandle):
                fileStats.addLen(len(seq))


    def plot2DFigure(self, fileName="", groupNames=[]):
        '''Plot the data, arranged via groups

        Inputs:
         fileName - string, name of the file to write the image to
         groupNames - [string], group names used in legend

        Outputs:
         None
        '''

        # set colors here
        col_set = "qualPaired"
        cb2 = CB2()
        colours = cb2.maps[col_set].values()
        fg_cols = [7,3,9,1]
        fg_style = '-'
        bg_cols = [6,2,8,0]
        bg_style = '--'

        def smooth(y, window):
            '''Simple windowed mean smoother'''
            # window is odd
            if window %2 == 0:
                window += 1
            mid_index = int(window/2)
            tote_len = len(y)
            mx_idx = tote_len -1
            ret = []
            start = -1 * mid_index
            end = start + window

            for _ in range(tote_len):
                ts = start if start >= 0 else 0
                te = end if end <= mx_idx else mx_idx
                ret.append(np.mean(y[ts:te]))
                start += 1
                end = start + window
            return np.array(ret)

        # first get the data to plot
        data = []
        plt_file_names = self.fileStats.keys()
        for plt_file_name in plt_file_names:
            data.append(self.fileStats[plt_file_name].getDistInfo())
        data = np.array(data)

        # align the min and max values
        g_min = sys.maxint
        g_max = 0
        for d in data:
            if d[0][0] < g_min:
                g_min = d[0][0]
            if d[-1][0] > g_max:
                g_max = d[-1][0]

        # plot synced data
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plot_xs = np.arange(g_min, g_max+1)
        # only need one legend for each group
        seen_groups = {}
        for fn_idx in range(len(plt_file_names)):
            d = data[fn_idx]
            group = self.file2Groups[plt_file_names[fn_idx]]
            fg_label = ''
            bg_label = ''
            if groupNames != []:
                if group not in seen_groups:
                    seen_groups[group] = True
                    fg_label = "%s (smoothed)" % groupNames[group]
                    bg_label = "%s (actual)" % groupNames[group]
            plot_ys = np.zeros(g_max-g_min+1)
            for [l, c] in d:
                plot_ys[l-g_min] = c
            fg_col = colours[fg_cols[group]]
            bg_col = colours[bg_cols[group]]
            ax.plot(plot_xs,
                    plot_ys,
                    ls=bg_style,
                    color=bg_col,
                    label=bg_label)
            ax.plot(plot_xs,
                    smooth(plot_ys, 7),
                    ls=fg_style,
                    color=fg_col,
                    label=fg_label)

        if groupNames != []:
            ax.legend(loc='upper left')

        ax.set_xlim([g_min, g_max])

        plt.xlabel("Sequence length")
        plt.ylabel("Count")

        plt.tight_layout()

        # show figure
        if fileName == "":
            plt.show()
        else:
            # or save figure
            plt.savefig(fileName, dpi=300, format='png')
        plt.close(fig)
        del fig

    def __str__(self):
        '''Override print functions'''
        for fn, fs in self.fileStats.items():
            return "%s\n%s" % (fn, str(fs))

