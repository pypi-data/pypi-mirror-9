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

__author__ = "Luís Martinho <lmartinho@hive.pt>"
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

configurations = (
    {
        "recursive" : True,
        "source_encoding" : "Cp1252",
        "target_encoding" : "utf-8",
        "windows_newline" : True,
        "replacements_list" : (),
        "file_extensions" : (
            "js",
            "php",
            "cs",
            "java",
            "cpp",
            "c",
            "m",
            "hpp",
            "h",
            "pch",
            "cs",
            "st",
            "ctp",
            "xml",
            "xsd",
            "html",
            "xhtml",
            "wiki",
            "wik",
            "prl",
            "json",
            "txt",
            "hxml",
            "hx",
            "as",
            "mxml",
            "bat",
            "tpl",
            "vcproj",
            "csproj",
            "sln",
            "strings",
            "conf",
            "luquid",
            "go",
            "md"
        ),
        "file_exclusion" : ("android-sdk",)
    },
    {
        "recursive" : True,
        "source_encoding" : "Cp1252",
        "target_encoding" : "utf-8",
        "windows_newline" : True,
        "replacements_list" : (
            (
                "# -*- coding: Cp1252 -*-\n",
                "# -*- coding: utf-8 -*-\n"
            ),
        ),
        "file_extensions" : (
            "py",
        ),
        "file_exclusion" : ("android-sdk",)
    },
    {
        "recursive" : True,
        "source_encoding" : "Cp1252",
        "target_encoding" : "utf-8",
        "windows_newline" : True,
        "replacements_list" : (
            (
                "# encoding: Cp1252\n",
                "# encoding: utf-8\n"
            ),
        ),
        "file_extensions" : (
            "rb",
        ),
        "file_exclusion" : ("android-sdk",)
    },
    {
        "recursive" : True,
        "source_encoding" : "Cp1252",
        "target_encoding" : "utf-8",
        "windows_newline" : True,
        "replacements_list" : (
            (
                "@charset \"Cp1252\";\n",
                "@charset \"utf-8\";\n",
            ),
        ),
        "file_extensions" : (
            "css",
        ),
        "file_exclusion" : ("android-sdk",)
    },
    {
        "recursive" : True,
        "source_encoding" : "Cp1252",
        "target_encoding" : "utf-8",
        "windows_newline" : True,
        "replacements_list" : (
            (
                "encoding/<project>=Cp1252\n",
                "encoding/<project>=utf-8\n",
            ),
        ),
        "file_extensions" : (
            "prefs",
        ),
        "file_exclusion" : ("android-sdk",)
    },
    {
        "recursive" : True,
        "source_encoding" : "Cp1252",
        "target_encoding" : "utf-8",
        "windows_newline" : False,
        "replacements_list" : (
            (
                "# -*- coding: Cp1252 -*-\n",
                "# -*- coding: utf-8 -*-\n"
            ),
        ),
        "file_extensions" : (
            "sh",
            "drg",
            "am",
            "m4"
        ),
        "file_exclusion" : ("android-sdk",)
    }
)
