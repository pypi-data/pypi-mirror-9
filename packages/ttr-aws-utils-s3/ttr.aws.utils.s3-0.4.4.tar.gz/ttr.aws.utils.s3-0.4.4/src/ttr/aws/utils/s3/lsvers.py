# Copyright (c) 2011, Jan Vlcinsky
# Copyright (c) 2012, TamTam Research s.r.o. http://www.tamtamresearch.com
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of the FreeBSD Project.

import boto
import argparse
import sys
import datetime
import itertools
import dateutil.parser
import calendar
import plac
import os
import json
from csv import DictWriter
from ConfigParser import SafeConfigParser

from pkg_resources import resource_string
templ = resource_string(__name__, 'chart.html')


def load_alias(bucket_key):
    config = SafeConfigParser()
    rcfname = ".s3lsversrc"
    flocs = [os.curdir, os.path.expanduser("~"), "/etc/s3lsvers"]
    config.read([os.path.join(loc, rcfname) for loc in flocs])
    return config.get("aliases", bucket_key)


def get_json_record(dtime, size, age):
    tt = datetime.datetime.timetuple(dtime)
    epoch = calendar.timegm(tt) * 1000
    return [epoch, size, age]


@plac.annotations(
    profile_name=("""Name of boto profile to use for credentials""", "option"),
    aws_access_key_id=("Your AWS Access Key ID", "option"),
    aws_secret_access_key=("Your AWS Secret Access Key", "option"),
    from_time=(
        """Modification time of oldest expected version as ISO 8601 format.
        Can be truncated. (default: goes to the oldest version)""",
        "option", "from"),
    to_time=(
        """Modification time of youngest expected version as ISO 8601 format.
        Can be truncated. (default: goes to the latest version)""",
        "option", "to"),
    list_file=(
        """Name of file, where is result written in csv format.
        If set, the file is always overwritten.""",
        "option", None, argparse.FileType("wb")),
    html_file=(
        """Name of file, where is result written in html format (as a chart).
        If set, the file is always overwritten.""",
        "option", None, argparse.FileType("wb")),
    version_id=('''Optional version-id.
        If specified, listing does not start from the freshest version,
        but starts searching from given VERSION_ID
        and continues searching older and older versions.
        This could speed up listng in case, you need rather older files
        and you know VERSION_ID which came somehow later
        then is the time scope you are going to list.''',
                "option"),
    bucket_key=("bucket_name/key_name for the key to list, or key alias defined in .s3lsvers file", "positional")
)
def main(bucket_key, from_time=None, to_time=None,
         list_file=None, html_file=None, version_id=None, profile_name=None,  aws_access_key_id=None,
          aws_secret_access_key=None):
    """Lists all versions of given key, possibly filtering by from - to range
    for version last_modified time.
    Allows to put the listing into csv file and or into html chart.

        Listing shows:
          key_name
            "file name". Can repeat if the file has more versions

          version_id
            unique identifier for given version on given bucket.  Has form of
            string and not a number. identifiers are "random", do not expect
            that they are sorten alphabetically.

          size
            size of file in bytes

          last_modified
            ISO 8601 formated time of file modification,
            e.g. `2011-06-22T03:05:09.000Z`

          age
            difference between last_modified or given version
            and preceding version. It is sort of current
            update interval for that version.

        Sample use:
        Lists to the screen all versions of file keyname in the
        bucketname bucket::

            $ s3lsvers bucketname/keyname

        Lists all versions younger then given time (from given time till now)::

            $ s3lsvers -from 2011-07-19T12:00:00 bucketname/keyname

        Lists all versions older then given time
        (from very first version till given date)::

            $ s3lsvers -to 2011-07-19T12:00:00 bucketname/keyname

        Lists all versions in period betwen from and to time::

            $ s3lsvers -from 2010-01-01 -to 2011-07-19T12:00:00 \
            bucketname/keyname

        Lists all versions and writes them into csv file named versions.csv::

            $ s3lsvers -list-file versions.csv bucketname/keyname

        Lists all versions and writes them into html chart file
        named chart.html::

            $ s3lsvers -html-file chart.html bucketname/keyname

        Prints to screen, writes to csv, creates html chart and this all
        for versions in given time period.::

            $ s3lsvers -from 2010-01-01 -to 2011-07-19T12:00:00 \
            -list-file versions.csv -html-file chart.html bucketname/keyname

        Using bucket/key_name aliases in .s3lsvers file

        Instead of using long bucket and key names on command line, you may define aliases.

        Aliases are specified in file .s3lsvers, which may be located in currect directory, home directory or /etc/s3lsvers"

        Content of .s3lsvers files may look like this::

            #.s3lsversrc - definition of some preconfigured bucket/key values
            [DEFAULT]
            pl-base: pl-base.dp.tamtamresearch.com
            cz-base: cz-base.dp.tamtamresearch.com
            sk-base: sk-base.dp.tamtamresearch.com

            #values left to ":" must not contain "/" to prevent confusion with real bucket names
            [aliases]
            plcsr: %(pl-base)s/region/pl/ConsumerServiceReady.xml
            pldfs: %(pl-base)s/region/pl/DataFusionService.xml
            czcsr: %(cz-base)s/region/cz/ConsumerServiceReady.xml
            czdfs: %(cz-base)s/region/cz/DataFusionService.xml
            skcsr: %(sk-base)s/region/sk/ConsumerServiceReady.xml
            skdfs: %(sk-base)s/region/sk/DataFusionService.xml
            skes: %(sk-base)s/region/sk/EventService.xml
            sksr: %(sk-base)s/region/sk/SummaryReports.xml

        The format follows SafeConfigParser rules: http://docs.python.org/2/library/configparser.html#safeconfigparser-objects

    """

    if ("/" not in bucket_key):
        bucket_key = load_alias(bucket_key)
    assert "/" in bucket_key, "bucket_key must be in form 'bucket/key_name'"
    bucket_name, key_name = bucket_key.split("/", 1)
    cmdname = os.path.basename(sys.argv[0])
    if (from_time and to_time) and (from_time > to_time):
        msg = "-from ({from_time}) must be smaller then -to ({to_time})"
        print msg.format(**locals())
        return

    conn = boto.connect_s3(profile_name=profile_name, aws_access_key_id= aws_access_key_id, aws_secret_access_key= aws_secret_access_key)

    bucket = conn.get_bucket(bucket_name)
    try:
        if version_id is None:  # todo
            raise NameError
        versions = bucket.list_versions(
            key_name, key_marker=key_name, version_id_marker=version_id)
    except NameError:
        versions = bucket.list_versions(key_name)
    try:
        json_data = []
        if list_file:
            fields = ["key_name", "version_id", "size", "last_modified", "age"]
            csvwriter = DictWriter(
                list_file, fields, delimiter=";", extrasaction="ignore")
        for ver in vergen(versions, from_time, to_time, working, 600):
            print "Date: {last_modified} Size: {size} Age: {age}".format(**ver)
            if list_file:
                try:
                    csvwriter.writerow(ver)
                except Exception as e:
                    print e
                    raise
            if html_file:
                json_data.append(get_json_record(ver[
                                 "atime"], ver["size"], ver["age"]))

        if html_file:
            title = "{bucket_name}:{key_name}".format(**locals())
            json_data = json.dumps(json_data, separators=(",", ":"))
            res = render_html(json_data, title=title)
            html_file.write(res)
    except KeyboardInterrupt:
        print "...cancelled."
        pass
    finally:
        try:
            list_file.close()
        except:
            pass
        try:
            html_file.close()
        except:
            pass
    return


def working(ver):
    print "version num: {i}, modified: {last_modified}".format(**ver)


def vergen(versions, from_time, to_time, callback=None, callback_after=600):
    """return data
    atime, ka.size. age
    ka.name, ka.version_id, ka.size, ka.last_modified, age

    """
    vers_a, vers_b = itertools.tee(versions)
    vers_b.next()

    def buildver():
        """create dict, describing one version of key"""
        return {"i": i, "atime": atime, "btime": btime, "age": age,
                "key_name": ka.name, "size": ka.size,
                "last_modified": ka.last_modified, "version_id": ka.version_id
                }
    for i, ka, kb in itertools.izip(itertools.count(), vers_a, vers_b):
        last_modified = ka.last_modified
        atime = dateutil.parser.parse(last_modified)
        btime = dateutil.parser.parse(kb.last_modified)
        age = (atime - btime).seconds
        if from_time and (last_modified < from_time):
            break
        elif to_time and (last_modified > to_time):
            if i % callback_after == 0:
                callback(buildver())
            continue
        yield buildver()


def render_html(json_data, title,
                subtitle="(gzipped) feed size [bytes] and update intervals[seconds]",
                set_1_name="Feed size", set_2_name="Update iterval", ):
    return templ.format(**locals())


def placer():
    try:
        plac.call(main)
    except Exception as e:
        print e

if __name__ == "__main__":
    placer()
