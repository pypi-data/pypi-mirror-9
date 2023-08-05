# Read marker files created by `notify-reboot-required` of the
# `update-notifier-common` package. These indicate that a package has
# requested the machine to be rebooted at a convenient time.

from datetime import datetime, date
from fileinput import FileInput
import os
import re
import sys

from plugins.output import (CheckException,
                            nagios_ok,
                            nagios_warning,
                            nagios_critical,
                            nagios_unknown,
                            nagios_message)


def dpkg_log_lines(log_files):
    """Parse the package install logs into a list of lines"""
    valid_log_files = []
    for log_file in log_files:
        if os.path.exists(log_file):
            valid_log_files.append(log_file)
    if len(valid_log_files) > 0:
        try:
            return list(FileInput(valid_log_files))
        except:
            nagios_unknown("Cannot find/open the dpkg log files")
    else:
        nagios_unknown("None of the listed dpkg log files are available")


def grep(string, list):
    """Find a string within a list of lines"""
    expr = re.compile(string)
    return [elem for elem in list if expr.match(elem)]


def parse_files(warning_days, critical_days,
                dpkg_log_files=['/var/log/dpkg.log.1', '/var/log/dpkg.log'],
                reboot_required_file='/var/run/reboot-required',
                reboot_required_pkgs_file='/var/run/reboot-required.pkgs'):
    full_message = ""
    install_dates = []
    dpkg_log = dpkg_log_lines(dpkg_log_files)

    # Check if the reboot-required flag file exists
    # To silence the check, delete this file
    if not os.path.exists(reboot_required_file):
        nagios_ok("Reboot required file (%s) does not exist" %
                  reboot_required_file)

    if not os.path.exists(reboot_required_pkgs_file):
        nagios_ok("No packages listed requiring reboot")
    with open(reboot_required_pkgs_file) as f:
        # for each package, attempt to find what time it was installed
        for line in f.readlines():
            package = line.rstrip()
            log_lines = grep(".*status installed %s.*" %
                             package, dpkg_log)
            if len(log_lines) >= 1:
                install_date = log_lines[0].split(' ')[0]
            else:
                # This is a nasty nasty hack. If I can't find the install
                # date in the dkpg log, (for whatever reason), I still
                # want to reboot to install that package,
                # so I will fake the date. Later on I will
                # check the date and if I find the minimum is 2199-12-12,
                # I will go UNKNOWN instead.
                install_date = '2199-12-12'
            full_message += "%s: %s\n" % (install_date, package)
            install_dates.append(install_date)

    # Find the age in days of the oldest package install
    if min(install_dates) == '2199-12-12':
        nagios_unknown('There are packages requiring reboot that I can '
                       'find no install date for, so I have assumed '
                       '2199-12-12\n\n%s' % full_message)
    oldest_install_date = datetime.strptime(min(install_dates),
                                            "%Y-%m-%d").date()
    today = date.today()
    install_age = today - oldest_install_date

    # Spit out the correct message
    if int(install_age.days) >= int(critical_days):
        nagios_critical("Packages requiring reboot outstanding for longer "
                        "than %s days:\n\n%s"
                        % (critical_days, full_message.rstrip()))
    elif int(install_age.days) >= int(warning_days):
        nagios_warning("Packages requiring reboot outstanding for longer "
                       "than %s days:\n\n%s"
                       % (warning_days, full_message.rstrip()))
    else:
        nagios_ok("Packages requiring reboot, but inside the threshold of "
                  "%s days\n\n%s" % (warning_days, full_message.rstrip()))


usage_message = """
Usage: ./check_reboot_required [critical_days] [warning_days]

When given no arguments, the default threshold is 0 days.
One argument will raise a critical alert at that number of days.
Two arguments will raise a warning at the first number of days
and a critical at the second number of days
"""


def main():
    try:
        if len(sys.argv) >= 3:
            warning_days = sys.argv[2]
            critical_days = sys.argv[1]
        elif len(sys.argv) == 2:
            if sys.argv[1] == "-h":
                print usage_message
                sys.exit(0)
            else:
                warning_days = sys.argv[1]
                critical_days = sys.argv[1]
        else:
            warning_days = 0
            critical_days = 0

        parse_files(warning_days, critical_days)

    except CheckException as e:
        nagios_message(e.message, e.severity)
    except Exception as e:
        # Catching all other exceptions
        nagios_message("Exception: %s" % e, 3)
