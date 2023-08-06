# -- coding: utf-8 --

# Copyright 2015 Tim Santor
#
# This file is part of proprietary software and use of this file
# is strictly prohibited without written consent.
#
# @author  Tim Santor  <tsantor@xstudios.agency>

# -----------------------------------------------------------------------------

import argparse
import uuid
import csv

from subprocess import Popen, PIPE
import os, sys, getopt
import platform
import re

# ensure path is in sys path
#new_path = "../bashutils"
#if new_path not in sys.path:
#    sys.path.append(new_path)

from bashutils import *

# -----------------------------------------------------------------------------

class Main(object):

    def check_requirements(self):
        if not cmd_exists('convert'):
            e_error('ImageMagick is not installed')
            sys.exit()


    def get_list_from_csv(self):
        """
        Open and read a CSV into a list using the column headers as key names.
        """
        try:
            f = open(self.inputfile, 'rU')
            csv_f = list(csv.DictReader(f))
            f.close()
            return csv_f
        except BaseException, e:
            #e_error(e)
            sys.exit(e)


    def create_psd(self, size, filename=None):
        """
        Create a blank PSD file at a specific size.

        :param str size: width x height (eg - 300x250)
        :param str filename: output file name
        :rtype bool:
        """
        if filename is None:
            filename = size

        # create a 8bit RGB 72 dpi blank PSD (color BG to force RGB as white or black
        # will cause it to be grayscale due to lack of color)
        cmd = "convert \
                -size %s xc:wheat \
                -colorspace RGB \
                -depth 8 \
                -units pixelsperinch \
                -density 72 \
                %s.psd" % (size, filename)
        return exec_cmd(cmd)


    def generate_filename(self, row):
        """
        Generates a filename given a row from the manifest CSV.
        """
        size = '{0}x{1}'.format(row['Width'], row['Height'])
        prefix = row['Prefix']
        suffix = row['Suffix']

        if prefix:
            prefix = '{0}_'.format(prefix)

        if suffix:
            suffix = '_{0}'.format(suffix)

        filename = '{0}{1}{2}'.format(prefix, size, suffix)
        return filename


    def generate_psds(self):
        """
        Generates PSDs from manifest CSV.
        """
        num_files = 0

        for row in self.csv_data:
            if row['Type'] not in ['Flash'] and (row['Width'] and row['Height']):
                size = '{0}x{1}'.format(row['Width'], row['Height'])
                filename = self.generate_filename(row)
                if self.verbose: print '{0} with filename {1}'.format(size, filename+'.psd')
                self.create_psd(size, self.output_dir+filename)
                num_files += 1

        return num_files


    def zip_files(self):
        filename = uuid.uuid4()
        cmd = 'zip -r {0}.zip {1}'.format(filename, self.output_dir)
        return exec_cmd(cmd)


    def get_args(self):
        # https://docs.python.org/2/howto/argparse.html
        parser = argparse.ArgumentParser(description="Generate PSDs")

        # positional arguments
        parser.add_argument("input", help="input file (.csv)")
        parser.add_argument("output", help="output directory")

        # optional arguments
        parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")

        # Add group of optional arguments that conflict with one another
        #group = parser.add_mutually_exclusive_group()
        #group.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
        #group.add_argument("-q", "--quiet", help="no verbose output", action="store_true")

        # parse our arguments
        return parser.parse_args()


    def run(self):
        # Ensure proper command line usage
        args = self.get_args()

        # set class properties
        self.inputfile  = args.input
        self.output_dir = os.path.join(args.output, '')
        self.verbose    = args.verbose

        # Check requirements
        self.check_requirements()

        # Open the CSV
        e_header('Get deliverables data from CSV...')
        self.csv_data = self.get_list_from_csv()

        # Delete and create the dir we need
        # (don't want any residual files from previous runs)
        if dir_exists(self.output_dir):
            if confirm('"%s" already exists. Delete it' % self.output_dir):
                delete_dir(self.output_dir)
        ensure_dir(self.output_dir)

        e_header('Generating PSDs...')
        num_files = self.generate_psds()

        #e_header('Zipping up PSDs...')
        #zip_files(output_dir)

        e_success('Generated {0} PSD files'.format(num_files))

# -----------------------------------------------------------------------------

def main():
    main = Main()
    main.run()

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
