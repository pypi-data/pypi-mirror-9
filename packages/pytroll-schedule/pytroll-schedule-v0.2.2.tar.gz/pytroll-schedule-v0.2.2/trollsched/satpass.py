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

"""Satellite passes.
"""

import logging
import logging.handlers
import os
import operator
from datetime import datetime, timedelta
import numpy as np
from pyorbital import tlefile, orbital
from tempfile import mkstemp
from trollsched.boundary import SwathBoundary, AreaDefBoundary
import glob

logger = logging.getLogger(__name__)

# shortest allowed pass in minutes
MIN_PASS = 4


class Mapper(object):

    """A class to generate nice plots with basemap.
    """

    def __init__(self):
        from mpl_toolkits.basemap import Basemap

        self.map = Basemap(projection='nsper', lat_0=20, lon_0=40,
                           resolution='l', area_thresh=1000.)

        self.map.drawcoastlines()
        self.map.drawcountries()

        self.map.drawmapboundary(fill_color='white')

        self.map.drawmeridians(np.arange(0, 360, 30))
        self.map.drawparallels(np.arange(-90, 90, 30))

    def __enter__(self):
        return self.map

    def __exit__(self, etype, value, tb):
        pass

# Platform name to tle names translator
tle_names = {"Metop-A": "METOP-A",
             "Metop-B": "METOP-B",
             "NOAA-15": "NOAA 15",
             "NOAA-18": "NOAA 18",
             "NOAA-19": "NOAA 19",
             "Suomi-NPP": "SUOMI NPP",
             "EOS-Terra": "TERRA",
             "EOS-Aqua": "AQUA"}


class Pass(object):

    """A pass: satellite, risetime, falltime, (orbital)
    """

    buffer = timedelta(minutes=2)

    def __init__(self, satellite, risetime, falltime, orb=None, uptime=None, instrument=None):

        self.satellite = satellite
        self.risetime = risetime
        self.falltime = falltime
        self.uptime = uptime
        self.instrument = instrument
        self.orb = orb or orbital.Orbital(tle_names.get(satellite,
                                                        satellite))
        self.score = {}
        self.boundary = SwathBoundary(self)
        # make boundary lighter.
        # self.boundary.decimate(100)
        self.subsattrack = {"start": None,
                            "end": None}
        self.rec = False
        self.fig = None

    def overlaps(self, other, delay=timedelta(seconds=0)):
        """Check if two passes overlap in time.
        """
        return ((self.risetime < other.falltime + delay) and
                (self.falltime + delay > other.risetime))

    def __cmp__(self, other):
        if self.uptime < other.uptime:
            return -1
        if self.uptime > other.uptime:
            return 1
        else:
            return 0

    def __eq__(self, other):
        return (self.risetime == other.risetime and
                self.falltime == other.falltime and
                self.satellite == other.satellite)

    def __str__(self):
        return (self.satellite + " "
                + self.risetime.isoformat() + " " + self.falltime.isoformat())

    def __repr__(self):
        return str(self)

    def duration(self):
        """Get the duration of an overpass.
        """
        return self.falltime - self.risetime

    def seconds(self):
        """Get the duration of an overpass.
        """
        duration = self.duration()
        return (duration.days * 24 * 60 * 60
                + duration.seconds
                + duration.microseconds * 1e-6)

    def pass_direction(self):
        """Get the direction of the pass in (ascending, descending).
        """
        start_lat = self.orb.get_lonlatalt(self.risetime)[1]
        end_lat = self.orb.get_lonlatalt(self.falltime)[1]

        if start_lat > end_lat:
            return "descending"
        else:
            return "ascending"

    def slsearch(self, sublat):
        """Find sublatitude.
        """

        def nadirlat(minutes):
            return self.orb.get_lonlatalt(self.risetime +
                                          timedelta(minutes=np.float64(minutes)))[1] - sublat

        def get_root(fun, start, end):
            p = np.polyfit([start, (start + end) / 2.0, end],
                           [fun(start), fun((start + end) / 2), fun(end)],
                           2)
            for root in np.roots(p):
                if root <= end and root >= start:
                    return root

        arr = np.array([nadirlat(m) for m in range(15)])
        a = np.where(np.diff(np.sign(arr)))[0]
        for guess in a:
            sublat_mins = get_root(nadirlat, guess, guess + 1)
            return self.risetime + timedelta(minutes=sublat_mins)

    def area_coverage(self, area_of_interest):
        """Get the ratio of coverage (between 0 and 1) of the pass with the area
        of interest.
        """
        try:
            area_boundary = area_of_interest.poly
        except AttributeError:
            area_boundary = AreaDefBoundary(area_of_interest,
                                            frequency=500)
            area_boundary = area_boundary.contour_poly
        inter = self.boundary.contour_poly.intersection(
            area_boundary)
        if inter is None:
            return 0
        return inter.area() / area_boundary.area()

    def save_fig(self, poly=None, directory="/tmp/plots",
                 overwrite=False, labels=None, extension=".png"):
        """Save the pass as a figure. Filename is automatically generated.
        """
        logger.debug("Save fig " + str(self))
        rise = self.risetime.strftime("%Y%m%d%H%M%S")
        fall = self.falltime.strftime("%Y%m%d%H%M%S")
        filename = os.path.join(directory,
                                (rise + self.satellite + fall + extension))

        self.fig = filename
        if not overwrite and os.path.exists(filename):
            return filename

        import matplotlib.pyplot as plt
        plt.clf()
        with Mapper() as mapper:
            mapper.nightshade(self.uptime, alpha=0.2)
            self.draw(mapper, "-r")
            if poly is not None:
                poly.draw(mapper, "-b")
        plt.title(str(self))
        for label in labels or []:
            plt.figtext(*label[0], **label[1])
        plt.savefig(filename)
        return filename

    def show(self, poly=None, labels=None, other_poly=None):
        """Show the current pass on screen (matplotlib, basemap).
        """
        import matplotlib.pyplot as plt
        plt.clf()
        with Mapper() as mapper:
            mapper.nightshade(self.uptime, alpha=0.2)
            self.draw(mapper, "-r")
            if poly is not None:
                poly.draw(mapper, "-b")
            if other_poly is not None:
                other_poly.draw(mapper, "-g")
        plt.title(str(self))
        for label in (labels or []):
            plt.figtext(*label[0], **label[1])
        plt.show()

    def draw(self, mapper, options):
        """Draw the pass to the *mapper* object (basemap).
        """
        self.boundary.contour_poly.draw(mapper, options)

    def print_vcs(self, coords):
        """Should look like this::


#SCName          RevNum Risetime        Falltime        Elev Dura ANL   Rec Dir Man Ovl OvlSCName        OvlRev OvlRisetime     OrigRisetime    OrigFalltime    OrigDuration
#
NOAA 19           24845 20131204 001450 20131204 003003 32.0 15.2 225.6 Y   Des N   N   none                  0 19580101 000000 20131204 001450 20131204 003003 15.2


        """

        max_elevation = self.orb.get_observer_look(self.uptime, *coords)[1]
        anl = self.orb.get_lonlatalt(
            self.orb.get_last_an_time(self.risetime))[0] % 360
        #anl = self.orb.get_observer_look(self.risetime, *coords)[0]
        if self.rec:
            rec = "Y"
        else:
            rec = "N"
        line_list = ["{satellite:<16}",
                     "{orbit:>6}",
                     "{risetime}",
                     "{falltime}",
                     "{elevation:>4.1f}",
                     "{duration:>4.1f}",
                     "{anl:>5.1f}",
                     "{rec:<3}",
                     "{direction}",
                     "N   N   none                  0 19580101 000000",
                     "{risetime}",
                     "{falltime}",
                     "{duration:>4.1f}",
                     ]
        line = " ".join(line_list).format(
            satellite=self.satellite.upper(),
            orbit=self.orb.get_orbit_number(self.risetime),
            risetime=self.risetime.strftime("%Y%m%d %H%M%S"),
            falltime=self.falltime.strftime("%Y%m%d %H%M%S"),
            elevation=max_elevation,
            duration=(self.falltime - self.risetime).seconds / 60.0,
            anl=anl,
            rec=rec,
            direction=self.pass_direction().capitalize()[:3])
        return line

HOST = "ftp://is.sci.gsfc.nasa.gov/ancillary/ephemeris/schedule/aqua/downlink/"
import urlparse
import ftplib
import socket


def get_aqua_dumps_from_ftp(start_time, end_time, satorb):
    url = urlparse.urlparse(HOST)
    logger.debug("Connect to ftp server")
    try:
        f = ftplib.FTP(url.netloc)
    except (socket.error, socket.gaierror), e:
        logger.error('cannot reach to %s ' % HOST + str(e))
        f = None

    if f is not None:
        try:
            f.login('anonymous', 'guest')
            logger.debug("Logged in")
        except ftplib.error_perm:
            logger.error('cannot login anonymously')
            f.quit()
            f = None

    if f is not None:
        data = []
        try:
            f.dir(url.path, data.append)
        except socket.error, e:
            logger.error("Can't get any data: " + str(e))
            f.quit()
            f = None
        else:
            filenames = [line.split()[-1] for line in data]

    if f is None:
        logger.info("Can't access ftp server, using cached data")
        filenames = glob.glob("/tmp/*.rpt")

    dates = [datetime.strptime("".join(filename.split(".")[2:4]), "%Y%j%H%M%S")
             for filename in filenames]
    filedates = dict(zip(dates, filenames))

    dumps = []

    for date in sorted(dates):
        lines = []
        if not filedates[date].endswith(".rpt"):
            continue
        if not os.path.exists(os.path.join("/tmp", filedates[date])):
            f.retrlines(
                'RETR ' + os.path.join(url.path, filedates[date]), lines.append)
            with open(os.path.join("/tmp", filedates[date]), "w") as fd_:
                for line in lines:
                    fd_.write(line + "\n")
        else:
            with open(os.path.join("/tmp", filedates[date]), "r") as fd_:
                for line in fd_:
                    lines.append(line)

        for line in lines[7::2]:
            if line.strip() == '':
                break
            station, aos, elev, los = line.split()[:4]
            aos = datetime.strptime(aos, "%Y:%j:%H:%M:%S")
            los = datetime.strptime(los, "%Y:%j:%H:%M:%S")
            if los >= start_time and aos <= end_time:
                uptime = aos + (los - aos) / 2
                overpass = Pass("aqua", aos, los, satorb, uptime, "modis")
                overpass.station = station
                overpass.max_elev = elev
                dumps.append(overpass)
    if f is not None:
        f.quit()
    return dumps


def get_next_passes(satellites, utctime, forward, coords, tle_file=None):
    """Get the next passes for *satellites*, starting at *utctime*, for a
    duration of *forward* hours, with observer at *coords* ie lon (°E), lat
    (°N), altitude (km). Uses *tle_file* if provided, downloads from celestrack
    otherwise.
    """
    passes = {}
    orbitals = {}

    if tle_file is None:
        fp_, tle_file = mkstemp(prefix="tle", dir="/tmp")
        os.close(fp_)
        logger.info("Fetch tle info from internet")
        tlefile.fetch(tle_file)

    if not os.path.exists(tle_file):
        logger.info("Fetch tle info from internet")
        tlefile.fetch(tle_file)

    for sat in satellites:
        satorb = orbital.Orbital(sat, tle_file=tle_file)
        orbitals[sat] = satorb
        passlist = satorb.get_next_passes(utctime,
                                          forward,
                                          *coords)
        if sat.startswith("metop") or sat.startswith("noaa"):
            instrument = "avhrr"
        elif sat in ["aqua", "terra"]:
            instrument = "modis"
        elif sat.endswith("npp"):
            instrument = "viirs"
        else:
            instrument = "unknown"
        # take care of metop-a
        if sat == "metop-a":
            metop_passes = [Pass(sat, rtime, ftime, satorb, uptime, instrument)
                            for rtime, ftime, uptime in passlist]

            passes["metop-a"] = []
            for overpass in metop_passes:
                if overpass.pass_direction() == "descending":
                    new_rise = overpass.slsearch(60)
                    if new_rise is not None and new_rise < overpass.falltime:
                        overpass.risetime = new_rise
                        overpass.boundary = SwathBoundary(overpass)
                        if overpass.seconds() > MIN_PASS * 60:
                            passes["metop-a"].append(overpass)
        # take care of aqua (dumps in svalbard and poker flat)
        elif sat == "aqua":

            wpcoords = (-75.457222, 37.938611, 0)
            passlist_wp = satorb.get_next_passes(utctime - timedelta(minutes=30),
                                                 forward + 1,
                                                 *wpcoords)
            wp_passes = [Pass(sat, rtime, ftime, satorb, uptime, instrument)
                         for rtime, ftime, uptime in passlist_wp]

            svcoords = (15.399, 78.228, 0)
            passlist_sv = satorb.get_next_passes(utctime - timedelta(minutes=30),
                                                 forward + 1,
                                                 *svcoords)
            sv_passes = [Pass(sat, rtime, ftime, satorb, uptime, instrument)
                         for rtime, ftime, uptime in passlist_sv]
            pfcoords = (-147.43, 65.12, 0.51)
            passlist_pf = satorb.get_next_passes(utctime - timedelta(minutes=30),
                                                 forward + 1,
                                                 *pfcoords)
            pf_passes = [Pass(sat, rtime, ftime, satorb, uptime, instrument)
                         for rtime, ftime, uptime in passlist_pf]

            aqua_passes = [Pass(sat, rtime, ftime, satorb, uptime, instrument)
                           for rtime, ftime, uptime in passlist]

            dumps = get_aqua_dumps_from_ftp(utctime - timedelta(minutes=30),
                                            utctime +
                                            timedelta(hours=forward + 0.5),
                                            satorb)

            # remove the known dumps
            for dump in dumps:
                # print "*", dump.station, dump, dump.max_elev
                logger.debug("dump from ftp: " + str((dump.station, dump,
                                                      dump.max_elev)))
                for i, sv_pass in enumerate(sv_passes):
                    if sv_pass.overlaps(dump, timedelta(minutes=40)):
                        sv_elevation = sv_pass.orb.get_observer_look(sv_pass.uptime,
                                                                     *svcoords)[1]
                        logger.debug("Computed " + str(("SG", sv_pass,
                                                        sv_elevation)))
                        del sv_passes[i]
                for i, pf_pass in enumerate(pf_passes):
                    if pf_pass.overlaps(dump, timedelta(minutes=40)):
                        pf_elevation = pf_pass.orb.get_observer_look(pf_pass.uptime,
                                                                     *pfcoords)[1]
                        logger.debug("Computed " + str(("PF", pf_pass,
                                                        pf_elevation)))
                        del pf_passes[i]
                for i, wp_pass in enumerate(wp_passes):
                    if wp_pass.overlaps(dump, timedelta(minutes=40)):
                        wp_elevation = wp_pass.orb.get_observer_look(wp_pass.uptime,
                                                                     *wpcoords)[1]
                        logger.debug("Computed " + str(("WP", wp_pass,
                                                        wp_elevation)))
                        del wp_passes[i]

            # sort out dump passes first
            # between sv an pf, we take the one with the highest elevation if
            # pf < 20°, pf otherwise
            # I think wp is also used if sv is the only other alternative
            used_pf = []
            for sv_pass in sv_passes:
                found_pass = False
                for pf_pass in pf_passes:
                    if sv_pass.overlaps(pf_pass):
                        found_pass = True
                        used_pf.append(pf_pass)
                        sv_elevation = sv_pass.orb.get_observer_look(sv_pass.uptime,
                                                                     *svcoords)[1]
                        pf_elevation = pf_pass.orb.get_observer_look(pf_pass.uptime,
                                                                     *pfcoords)[1]
                        if pf_elevation > 20:
                            dumps.append(pf_pass)
                        elif sv_elevation > pf_elevation:
                            dumps.append(sv_pass)
                        else:
                            dumps.append(pf_pass)
                        break
                if not found_pass:
                    dumps.append(sv_pass)

            for pf_pass in pf_passes:
                if pf_pass not in used_pf:
                    dumps.append(pf_pass)

            passes["aqua"] = []
            for overpass in aqua_passes:
                add = True
                for dump_pass in dumps:
                    if dump_pass.overlaps(overpass):
                        if (dump_pass.uptime < overpass.uptime and
                                dump_pass.falltime > overpass.risetime):
                            logger.debug("adjusting " + str(overpass)
                                         + " to new risetime " +
                                         str(dump_pass.falltime))
                            overpass.risetime = dump_pass.falltime
                            overpass.boundary = SwathBoundary(overpass)
                        elif (dump_pass.uptime >= overpass.uptime and
                              dump_pass.risetime < overpass.falltime):
                            logger.debug("adjusting " + str(overpass)
                                         + " to new falltime " +
                                         str(dump_pass.risetime))
                            overpass.falltime = dump_pass.risetime
                            overpass.boundary = SwathBoundary(overpass)
                        if overpass.falltime <= overpass.risetime:
                            add = False
                            logger.debug("skipping " + str(overpass))
                if add and overpass.seconds() > MIN_PASS * 60:
                    passes["aqua"].append(overpass)

        else:
            passes[sat] = [Pass(sat, rtime, ftime, satorb, uptime, instrument)
                           for rtime, ftime, uptime in passlist
                           if ftime - rtime > timedelta(minutes=MIN_PASS)]

    return set(reduce(operator.concat, passes.values()))

if __name__ == '__main__':
    from trollsched.satpass import get_next_passes
    passes = get_next_passes(
        ["noaa 19", "suomi npp"], datetime.now(), 24, (16, 58, 0))
    for p in passes:
        p.save_fig(directory="/tmp/plots/")
