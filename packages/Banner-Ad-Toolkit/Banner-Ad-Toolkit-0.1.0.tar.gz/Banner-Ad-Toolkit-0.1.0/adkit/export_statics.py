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
import shutil

from subprocess import Popen, PIPE
import os, sys, getopt
import re

# ensure path is in sys path
#new_path = "../bashutils"
#if new_path not in sys.path:
#    sys.path.append(new_path)

from bashutils import *

# -----------------------------------------------------------------------------

class Main(object):

    def check_requirements(self):
        if not cmd_exists('pngquant'):
            e_error('pngquant is not installed')
            sys.exit()

        if not cmd_exists('convert'):
            e_error('ImageMagick is not installed')
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


    def convert_psds_to_pngs(self):
        """
        Loop through all files in the input directory and export them to PNGs,
        but only if they are PSDs.
        """
        # Loop through all files in input directory
        for fn in os.listdir( self.input_dir ):
            filename = self.input_dir + fn
            if os.path.isfile( filename ):

                # get filename and extension
                name, ext = os.path.splitext( filename )

                # if the file is a psd then convert it to a png
                if ext in ['.psd']:
                    self.convert_psd_to_png( filename )


    def convert_psd_to_png(self, filepath):
        """
        Convert a PSD to a PNG.
        """
        # get filename and extension
        basename = os.path.basename(filepath)
        name, ext = os.path.splitext(basename)

        output = '{0}{1}.png'.format(self.output_dir, name)

        cmd = 'convert "%s[0]" %s' % (filepath, output)
        return exec_cmd(cmd)


    def convert_to_jpg(self, filepath, max_size='40KB'):
        """
        Convert a file to a JPG.
        """
        # get filename and extension
        #basename = os.path.basename(filepath)
        name, ext = os.path.splitext(filepath)

        output = '{0}.jpg'.format(name)

        cmd = 'convert -quality 99 -define jpeg:extent={0} {1} {2}'.format(max_size, filepath, output)

        if exec_cmd(cmd):
            # delete source file
            os.remove(filepath)
            return True


    def png_crush(self):
        """
        Crush all the PNGs in the output directory to make them smaller.
        """
        cmd = "find %s -name '*.png' -exec pngquant --ext .png --force 256 {} \;" % self.output_dir
        return exec_cmd(cmd)


    def get_max_size(self, filepath):
        """
        Return string such as 40KB
        """
        size = self.get_size_from_filename(filepath)

        # get width height based on size string (eg - 300x250)
        width, height = size.split('x')

        # look in our CSV data for the banner matching this size
        for row in self.csv_data:
            if row['Type'] not in ['Flash'] and (row['Width'] == width and row['Height'] == height):
                if row['Max Size'] is not None and row['Max Size'] is not "":
                    if self.verbose: print '{0} must be less than {1}'.format(size, row['Max Size'])
                    return row['Max Size']
                else:
                    return None

        return None


    def get_size_from_filename(self, filepath):
        """
        Return string such as 300x250
        """
        p = re.compile( r'(\d{1,4}x\d{1,4})' )
        m = p.search( filepath )
        if m:
            return m.group()

        raise Exception("Unable to get size from filename!")


    def convert_string_size_to_bytes(self, string):
        """
        Convert 40KB to 40000 (bytes)
        """
        string = string.lower()

        if 'kb' in string:
            size = string.replace('kb', '')
            size = int(size) * 1000

        if 'mb' in string:
            size = string.replace('mb', '')
            size = int(size) * 100000

        if string is '' or string is None:
            return None

        return size


    def compress_to_max_size(self):
        """
        Loop through all files in the output directory and compress them so
        that they are under/at their max file size.
        """
        num_files = 0

        # Loop through all files in the output directory
        for fn in os.listdir( self.output_dir ):
            filepath = self.output_dir + fn
            if os.path.isfile( filepath ):
                # get filename and extension
                basename = os.path.basename(filepath)
                name, ext = os.path.splitext( basename )

                '''
                # if the png file is larger than the max size, convert to jpg at max size
                if ext in ['.png']:
                    max_size_string = selfget_max_size(filepath)

                    if max_size_string is None:
                        e_error('No max size specified for {0}'.format(fn))
                        continue

                    bytes = self.convert_string_size_to_bytes(max_size_string)

                    if os.path.getsize(fn) > bytes:
                        e_warning('{0} larger than {1}'.format(fn, max_size_string))
                        self.convert_to_jpg(fn, max_size_string)
                '''

                # compress to max size jpg
                max_size_string = self.get_max_size( filepath )

                if max_size_string is None:
                    e_error('No max size specified for {0}'.format( basename ))
                    continue

                #bytes = self.convert_string_size_to_bytes(max_size_string)

                #if os.path.getsize(filepath) > bytes:
                #    e_warning('{0} larger than {1}'.format(basename, max_size_string))
                #    self.convert_to_jpg(filepath, max_size_string)
                self.convert_to_jpg(filepath, max_size_string)

                num_files += 1

        return num_files


    def zip_files(self):
        filename = uuid.uuid4()
        cmd = 'zip -r {0}.zip {1}'.format(filename, self.output_dir)
        return exec_cmd(cmd)


    def get_args(self):
        # https://docs.python.org/2/howto/argparse.html
        parser = argparse.ArgumentParser(
            description="Export static jpgs from PSDs while ensure each is under or at a max file size."
        )

        # positional arguments
        parser.add_argument("manifest", help="input file (.csv)")
        parser.add_argument("input", help="input directory")
        parser.add_argument("output", help="output directory")

        # optional arguments
        parser.add_argument("-p", "--pngonly", help="export pngs only", action="store_true")
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

        self.input_file = args.manifest
        self.input_dir  = os.path.join(args.input, '')
        self.output_dir = os.path.join(args.output, '')
        self.verbose    = args.verbose

        # Check requirements
        self.check_requirements()

        # Open the CSV
        e_header('Get deliverables data from CSV...')
        self.csv_data = self.get_list_from_csv()

        # Delete and create the dir we need
        # (don't want any residual files from previous runs)
        delete_dir(self.output_dir)
        ensure_dir(self.output_dir)

        e_header('Convert PSDs to PNGs...')
        self.convert_psds_to_pngs()

        e_header('Crush PNGs (secret sauce)...')
        self.png_crush()

        # Stop here if png only
        if args.pngonly:
            e_success("DONE!")
            sys.exit()

        e_header('Ensure static files are no larger than max file size...')
        num_files = self.compress_to_max_size()

        #os.chdir(self.input_dir)
        #e_header('Zipping up Deliverables...')
        #self.zip_files()

        e_success('Compressed {0} files'.format(num_files))

# -----------------------------------------------------------------------------

def main():
    main = Main()
    main.run()

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
