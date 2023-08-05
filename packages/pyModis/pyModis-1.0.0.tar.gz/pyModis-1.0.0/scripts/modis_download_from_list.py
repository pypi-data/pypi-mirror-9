#!/usr/bin/env python
# Script to download massive MODIS data from a text file containing a list of
# MODIS file name
#
#  (c) Copyright Luca Delucchi 2013
#  Authors: Luca Delucchi
#  Email: luca dot delucchi at fmach dot it
#
##################################################################
#
#  This MODIS Python script is licensed under the terms of GNU GPL 2.
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
##################################################################
"""Script to download massive MODIS data from a text file containing a list of
MODIS file name"""
from datetime import date
try:
    from pymodis import optparse_gui
    WXPYTHON = True
except ImportError:
    WXPYTHON = False
from pymodis import downmodis
from pymodis import optparse_required
import sys


def main():
    """Main function"""
    # usage
    usage = "usage: %prog [options] destination_folder"
    if 1 == len(sys.argv) and WXPYTHON:
        option_parser_class = optparse_gui.OptionParser
    else:
        option_parser_class = optparse_required.OptionParser
    parser = option_parser_class(usage=usage,
                                 description='modis_download_from_list')
    # file
    parser.add_option("-f", "--file", dest="file", type='file',
                      help="Input file containing data to download")
    # url
    parser.add_option("-u", "--url", default="http://e4ftl01.cr.usgs.gov",
                      help="http/ftp server url [default=%default]",
                      dest="url")
    # password
    parser.add_option("-P", "--password", dest="password",
                      help="password to connect only if ftp server")
    # username
    parser.add_option("-U", "--username", dest="user", default="anonymous",
                      help="username to connect only if ftp server "
                      "[default=%default]")
    # path to add the path in the server
    parser.add_option("-s", "--source", dest="path", default="MOLT",
                      help="directory on the http/ftp server "
                      "[default=%default]")
    # path to add the url
    parser.add_option("-p", "--product", dest="prod", default="MOD11A1.005",
                      help="product name as on the http/ftp server "
                      "[default=%default]")
    # debug
    parser.add_option("-x", action="store_true", dest="debug", default=False,
                      help="this is useful for debugging the "
                      "download [default=%default]")
    # jpg
    parser.add_option("-j", action="store_true", dest="jpg", default=False,
                      help="download also the jpeg overview files "
                      "[default=%default]")
    # return options and argument
    (options, args) = parser.parse_args()
    if len(args) == 0 and not WXPYTHON:
        parser.print_help()
        sys.exit(1)
    if len(args) > 1:
        parser.error("You have to define the destination folder for HDF file")

    f = open(options.file)

    lines = [elem for elem in f.readlines()]

    tiles = [elem.strip().split('.')[2] for elem in lines if elem != '\n']
    tiles = ','.join(sorted(set(tiles)))
    dates = [elem.split('.')[1].replace('A', '') for elem in lines if elem != '\n']
    dates = sorted(set(dates))

    for d in dates:
        year = int(d[0:4])
        doy = int(d[4:7])
        fdate = date.fromordinal(date(year, 1, 1).toordinal() + doy - 1).isoformat()
        modisOgg = downmodis.downModis(url=options.url, user=options.user,
                                       password=options.password,
                                       destinationFolder=args[0],
                                       tiles=tiles, path=options.path,
                                       product=options.prod, delta=1,
                                       today=fdate, debug=options.debug,
                                       jpg=options.jpg)
        modisOgg.connect()
        day = modisOgg.getListDays()[0]
        if modisOgg.urltype == 'http':
            listAllFiles = modisOgg.getFilesList(day)
        else:
            listAllFiles = modisOgg.getFilesList()
        listFilesDown = modisOgg.checkDataExist(listAllFiles)
        modisOgg.dayDownload(day, listFilesDown)
        if modisOgg.urltype == 'http':
            modisOgg.closeFilelist()
        else:
            modisOgg.closeFTP()

if __name__ == "__main__":
    main()
