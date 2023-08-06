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

import os, sys
import platform
import re

from bashutils.logmsg import *
from bashutils.bashutils import *

# -----------------------------------------------------------------------------

class Main(object):

    def check_requirements(self):
        if not cmd_exists('convert'):
            log_error('ImageMagick is not installed')
            sys.exit()


    def get_list_from_csv(self):
        """
        Open and read a CSV into a list using the column headers as key names.
        """
        try:
            f = open(self.input_file, 'rU')
            csv_f = list(csv.DictReader(f))
            f.close()
            return csv_f
        except BaseException, e:
            #e_error(e)
            sys.exit(e)


    def create_psd(self, size, filepath):
        """
        Create a blank PSD file at a specific size.

        :param str size: width x height (eg - 300x250)
        :param str filepath: output file path
        :rtype bool:
        """
        # create a 8bit RGB 72 dpi blank PSD (color BG to force RGB as white or black
        # will cause it to be grayscale due to lack of color)
        cmd = 'convert \
                -size %s xc:wheat \
                -colorspace RGB \
                -depth 8 \
                -units pixelsperinch \
                -density 72 \
                "%s"' % (size, filepath)
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

        filename = '{0}{1}{2}.psd'.format(prefix, size, suffix)
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
                filepath = self.output_dir+filename

                # do not overwrite existing PSDs (that would be bad)
                if file_exists(filepath):
                    if self.verbose: log_warning('"{0}" already exists'.format(filename))
                    continue

                if self.verbose:
                    print 'Create {0} PSD with filename {1}'.format(size, filename)

                self.create_psd(size, filepath)
                num_files += 1

        return num_files


    def zip_files(self):
        """
        Zip output directory.
        """
        os.chdir(self.output_dir)
        filepath = "{0}{1}.zip".format(self.output_dir, uuid.uuid4())

        # quote path in case of spaces
        cmd = 'zip -r "{0}" .'.format( filepath )
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
        self.input_file = args.input
        self.output_dir = os.path.join(args.output, '')
        self.verbose    = args.verbose

        # Check requirements
        self.check_requirements()

        # Open the CSV
        log_header('Get deliverables data from CSV...')
        self.csv_data = self.get_list_from_csv()

        # Create the dir we need
        # (don't want any residual files from previous runs)
        #if dir_exists(self.output_dir):
        #    if confirm('"%s" already exists. Delete it' % self.output_dir):
        #        delete_dir(self.output_dir)
        make_dir(self.output_dir)

        log_header('Generating PSDs...')
        num_files = self.generate_psds()

        #log_header('Zipping up PSDs...')
        #zip_files(output_dir)

        log_success('Generated {0} PSD files'.format(num_files))

# -----------------------------------------------------------------------------

def main():
    main = Main()
    main.run()

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
