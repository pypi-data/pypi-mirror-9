#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014 Martin Raspaud

# Author(s):

#   Martin Raspaud <martin.raspaud@smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""get dump schedule from ftp.
"""

HOST = "ftp://is.sci.gsfc.nasa.gov/ancillary/ephemeris/schedule/aqua/downlink/"

import ftplib
import urlparse
import socket
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

def process_line(line):
    station, aos, elev, los = line.split()[:4]
    aos = datetime.strptime(aos, "%Y:%j:%H:%M:%S")
    los = datetime.strptime(los, "%Y:%j:%H:%M:%S")
#def main():
if __name__ == '__main__':
    url = urlparse.urlparse(HOST)
    try:
        f = ftplib.FTP(url.netloc)
    except (socket.error, socket.gaierror), e:
        logger.error('cannot reach to %s ' % HOST + str(e))
        #return

    logger.debug("Connect to ftp server")

    try:
        f.login('anonymous','guest')
    except ftplib.error_perm:
        logger.error('cannot login anonymously')
        f.quit()
        #return
    logger.debug("logged on to the ftp server")

    data = []

    f.dir(url.path, data.append)
    
    filenames = [line.split()[-1] for line in data]
    dates = [datetime.strptime("".join(filename.split(".")[2:4]), "%Y%j%H%M%S") for filename in filenames]
    filedates = dict(zip(dates, filenames))

    for date in sorted(dates, reverse=True):
        lines = []
        f.retrlines('RETR ' + os.path.join(url.path, filedates[date]), lines.append)

        for line in lines[7::2]:
            if line == '':
                break
            
        
        pause

    
    
#if __name__ == '__main__':
#    main()
