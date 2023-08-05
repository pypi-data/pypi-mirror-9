#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Administration Scripts
# Copyright (c) 2008-2015 Hive Solutions Lda.
#
# This file is part of Hive Administration Scripts.
#
# Hive Administration Scripts is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hive Administration Scripts is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hive Administration Scripts. If not, see <http://www.gnu.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2015 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

import os
import sys
import zlib
import time
import json
import struct
import getopt

import legacy

import admin_scripts.extra as extra

DEFAULT_COMPRESSION_LEVEL = 9
""" The default compression level, to be used
for the compression of gzip based files """

USAGE_MESSAGE = "join [-r] [-w exclusion_1, exclusion_2, ...] [-c configuration_file]"
""" The usage message """

def join_files(file_path):
    """
    Runs the joining operation according to the specification
    provided by the file located at the provided path.

    The joining operation may be complex and may take some
    time until it's completely finished.

    @type file_path: String
    @param file_path: The path to the file that contains the
    json based specification for the joining operation.
    """

    # normalizes the file path value so that it
    # represents a correct file path
    file_path_normalized = extra.normalize_path(file_path)

    # opens the file for reading and then reads the
    # complete set of data contained in it
    file = open(file_path_normalized, "rb")
    try: file_contents = file.read()
    finally: file.close()

    # uses the default encoding for json to decode
    # the complete set of contents in the file
    file_contents = file_contents.decode("utf-8")

    # loads the file contents, retrieving the
    # map of files to be created from joining
    files_map = json.loads(file_contents)

    # retrieves the directory path from the normalized
    # file path (for context resolution)
    directory_path = os.path.dirname(file_path_normalized)

    # tries to retrieve the target directories
    target_directories = files_map.get("_target_directories", None)

    # in case the target directories are
    # successfully retrieved
    if target_directories:
        # removes the target directories from
        # the files map (avoids collision)
        del files_map["_target_directories"]
    # otherwise the target directories to be
    # used are the default ones
    else:
        # sets the default target directories
        target_directories = (".",)

    # iterates over all the files (composition of joined files)
    # from the files map
    for file_key, file_value in files_map.items():
        # creates the string buffer for temporary
        # file holding, this is bytes based
        string_buffer = legacy.BytesIO()

        # retrieves the current value attributes
        # (setting default values)
        files = file_value.get("files", [])
        minify = file_value.get("minify", None)
        compress = file_value.get("compress", None)

        # sets the is first flag
        is_first = True

        # iterates over all the files,
        # to be joined
        for file in files:
            # in case it's the first file
            # no need to write the separator
            if is_first: is_first = False
            # otherwise the separator must
            # be written
            else: string_buffer.write(b"\r\n")

            # retrieves the complete file path by joining the
            # directory path and the current "file"
            file_path = os.path.join(directory_path, file)
            file_path = os.path.abspath(file_path)

            # in case the file does not exists, raises an
            # error indicating that there was an error
            if not os.path.exists(file_path):
                raise RuntimeError("the file path does not exist for file '%s'" % file)

            # opens the current file for reading
            # in binary format and reads the complete
            # set of contents into the current buffer
            _file = open(file_path, "rb")
            try: file_contents = _file.read()
            finally: _file.close()

            # writes the file contents into the string
            # buffer, appending the contents to the same file
            string_buffer.write(file_contents)

        # retrieves the string value from the buffer, this is
        # a binary (byte based) string and should be used with
        # the proper care to avoid unwanted results
        string_value = string_buffer.getvalue()

        # minifies and compresses the string value according
        # to the provided specification, some of this operations
        # may use complex third-party code
        string_value = minify == "javascript" and extra.javascript_minify(string_value) or string_value
        string_value = minify == "css" and extra.css_slimmer(string_value) or string_value
        string_value = compress == "gzip" and gzip_contents(string_value) or string_value

        # iterates over all the target directories for
        # to write the contents
        for target_directory in target_directories:
            # "calculates" the (current) base file path
            base_file_directory = os.path.join(directory_path, target_directory)
            base_file_directory = os.path.abspath(base_file_directory)
            base_file_path = os.path.join(base_file_directory, file_key)

            # in case the base file directory does not exists
            # it must be created
            if not os.path.exists(base_file_directory):
                # creates the base file directory
                os.makedirs(base_file_directory)

            # opens the base file for writing in binary
            base_file = open(base_file_path, "wb")

            try:
                # writes the final string value (after minification
                # and compression) to the base file
                base_file.write(string_value)
            finally:
                # closes the base file
                base_file.close()

def gzip_contents(contents_string, file_name = None):
    """
    Compresses the given contents using the deflate compression
    algorithm and encapsulating it into the gzip file format.

    @type contents_string: String
    @param contents_string: A string containing the contents
    to be compressed.
    @type file_name: String
    @param file_name: The name to be set to the file in the
    generated compressed buffer.
    @rtype: String
    @return: The string containing the compressed buffer.
    """

    # creates a new string buffer
    string_buffer = legacy.BytesIO()

    # writes the magic header and then writes the
    # compression method as part of binary header
    string_buffer.write(b"\x1f\x8b")
    string_buffer.write(b"\x08")

    # writes the flag values
    file_name and string_buffer.write(b"\x08") or string_buffer.write(b"\x00")

    # writes the timestamp value
    string_buffer.write(struct.pack("<L", legacy.LONG(time.time())))

    # writes some extra heading values
    # (includes operating system)
    string_buffer.write(b"\x02")
    string_buffer.write(b"\xff")

    # writes the file name
    file_name and string_buffer.write(file_name + b"\0")

    # compresses the contents with the zlib
    contents_string_compressed = zlib.compress(contents_string, DEFAULT_COMPRESSION_LEVEL)

    # writes the the contents string compressed into the string buffer
    string_buffer.write(contents_string_compressed[2:-4])

    # computes the contents string crc 32
    # and convert it to unsigned number
    contents_string_crc32 = zlib.crc32(contents_string)
    contents_string_crc32_unsigned = _unsigned(contents_string_crc32)

    # writes the crc 32 lower values
    string_buffer.write(struct.pack("<L", contents_string_crc32_unsigned))

    # retrieves the contents string size
    # and the writes the size lower values
    contents_string_length = len(contents_string)
    contents_string_length_unsigned = _unsigned(contents_string_length)
    string_buffer.write(struct.pack("<L", contents_string_length_unsigned))

    # retrieves the string value from the string buffer
    string_value = string_buffer.getvalue()

    # returns the string value
    return string_value

def _unsigned(number):
    """
    Converts the given number to unsigned assuming
    a 32 bit value.

    @type number: int
    @param number: The number to be converted to unsigned.
    @rtype: int
    @return: The given number converted to unsigned.
    """

    # in case the number is positive or zero
    # (no need to convert)
    if number >= 0:
        # returns the immediately with
        # the current number value
        return number

    # runs the modulus in the number
    # to convert it to unsigned
    return number + 4294967296

def join_files_walker(arguments, directory_name, names):
    """
    Walker method to be used by the path walker for the joining of the files.

    @type arguments: Tuple
    @param arguments: The arguments tuple sent by the walker method.
    @type directory_name: String
    @param directory_name: The name of the current directory in the walk.
    @type names: List
    @param names: The list of names in the current directory.
    """

    # unpacks the arguments tuple
    file_exclusion, = arguments

    # removes the complete set of names that are meant to be excluded from the
    # current set names to be visit (avoid visiting them)
    for exclusion in file_exclusion:
        if not exclusion in names: continue
        names.remove(exclusion)

    # retrieves the valid names for the names list (removes directory entries)
    valid_complete_names = [directory_name + "/" + name for name in names\
        if not os.path.isdir(directory_name + "/" + name)]

    # filters the names with non valid file extensions so that only the
    # ones that contain the join extension are used
    valid_complete_names = [os.path.normpath(name) for name in valid_complete_names\
        if len(name.split(".")) > 1 and name.split(".")[-2] == "join"\
        and name.split(".")[-1] == "json"]

    # iterates over all the valid complete names with extension filter
    for valid_complete_name in valid_complete_names:
        # print a message a message about the joining
        # operation that is going to be performed and
        # then runs the operation with the correct path
        extra.echo("Joining files defined in file: %s" % valid_complete_name)
        join_files(valid_complete_name)

def join_files_recursive(directory_path, file_exclusion):
    """
    Joins the files in recursive mode.
    All the options are arguments to be passed to the
    walker function.

    @type directory_path: String
    @param directory_path: The path to the (entry point) directory.
    @type file_exclusion: List
    @param file_exclusion: The list of file exclusion to be used.
    """

    legacy.walk(directory_path, join_files_walker, (file_exclusion,))

def main():
    """
    Main function used for the joining files.
    """

    # in case the number of arguments
    # is not sufficient
    if len(sys.argv) < 2:
        # prints a series of message related with he
        # correct usage of the command line and then
        # exits the process with error indication
        extra.echo("Invalid number of arguments")
        extra.echo("Usage: " + USAGE_MESSAGE)
        sys.exit(2)

    # sets the default values for the parameters
    path = sys.argv[1]
    recursive = False
    file_exclusion = None
    configuration_file_path = None

    try:
        options, _arguments = getopt.getopt(sys.argv[2:], "rw:c:", [])
    except getopt.GetoptError:
        # prints a series of messages about the
        # correct usage of the command line and
        # exits the current process with an error
        extra.echo("Invalid number of arguments")
        extra.echo("Usage: " + USAGE_MESSAGE)
        sys.exit(2)

    # iterates over all the options, retrieving the option
    # and the value for each
    for option, value in options:
        if option == "-r":
            recursive = True
        elif option == "-w":
            file_exclusion = [value.strip() for value in value.split(",")]
        elif option == "-c":
            configuration_file_path = value

    # retrieves the configurations from the command line arguments
    # either from the command line or configuration file
    configurations = extra.configuration(
        file_path = configuration_file_path,
        recursive = recursive,
        file_exclusion = file_exclusion
    )

    # iterates over all the configurations, executing them
    for configuration in configurations:
        # retrieves the configuration values
        recursive = configuration["recursive"]
        file_exclusion = configuration["file_exclusion"]

        # in case the recursive flag is set, joins the files in
        # recursive mode (multiple files)
        if recursive: join_files_recursive(path, file_exclusion)
        # otherwise it's a "normal" iteration and joins the
        # files (for only one file)
        else: join_files(path)

if __name__ == "__main__":
    main()
