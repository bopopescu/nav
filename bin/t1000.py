#!/usr/bin/env python
#
# Copyright 2008 Norwegian University of Science and Technology
#
# This file is part of Network Administration Visualized (NAV).
#
# NAV is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.  You should have received a copy of the GNU General Public License
# along with NAV. If not, see <http://www.gnu.org/licenses/>.
#

"""
t1000 finds blocked computers that have moved and blocks them again.

Usage:
sudo -u $NAV_USER ./t1000.py

t1000 is meant to be run as a cronjob. It checks the database for any
detained ports. If it finds any, it checks if the mac-address is active on
some other port and detains that port.

"""

import sys
import logging
import getpass
from datetime import datetime, timedelta

import nav.buildconf
from nav.arnold import (find_computer_info, disable, quarantine,
                        is_inside_vlans, NoDatabaseInformationError,
                        GeneralException, init_logging, open_port,
                        raise_if_detainment_not_allowed,
                        DetainmentNotAllowedError)
from nav.models.arnold import Identity, DetentionProfile

CONFIGFILE = nav.buildconf.sysconfdir + "/arnold/arnold.conf"

LOGGER = logging.getLogger('t1000')


def main():
    """Main controller"""
    init_logging(nav.buildconf.localstatedir + "/log/arnold/t1000.log")
    LOGGER.info("Starting t1000")

    # Fetch all mac-addresses that we have detained, check if they are
    # active somewhere else. As NAV collects arp and cam data periodically,
    # we need to give one hour slack to ensure data is correct.

    identities = Identity.objects.filter(
        last_changed__lte=datetime.now() - timedelta(hours=1),
        status__in=['disabled', 'quarantined'])

    if len(identities) <= 0:
        LOGGER.info("No detained ports in database where lastchanged > 1 "
                    "hour.")
        sys.exit(0)

    for identity in identities:
        LOGGER.info("%s is %s, checking for activity"
                    % (identity.mac, identity.status))
        try:
            candidate = find_computer_info(identity.mac)
        except NoDatabaseInformationError, error:
            LOGGER.info(error)
            continue

        # If this mac-address is active behind another port, block it.
        if candidate.endtime > datetime.now():
            if candidate.interface == identity.interface:
                LOGGER.info('Active on detained interface, will not pursue')
            else:
                pursue(identity, candidate)
        else:
            LOGGER.info("%s is not active." % candidate.mac)


def pursue(identity, candidate):
    """Try to detain this identity if applicable

    If profile says to not keep closed, we lift the detention for this
    identity after detaining the new interface. This also means that when
    detaining manually we keep all interfaces closed as this was the behavior
    in the old code.

    """
    LOGGER.info("%s is active on interface %s" % (
        candidate.mac, candidate.interface
    ))

    # Check if this reason is a part of any detention profile. If it is we
    # need to fetch the vlans from that profile and see if the new ip is on
    # one of those vlans or have to be skipped.

    profile = is_detained_by_profile(identity)
    if profile and not should_pursue(identity, profile):
        return

    try:
        raise_if_detainment_not_allowed(candidate.interface)
    except DetainmentNotAllowedError, error:
        LOGGER.error(error)
        return

    identity.autoenablestep = find_autoenable_step(identity)
    detain(identity, candidate)

    if profile and profile.keep_closed == 'n':
        try:
            open_port(identity, getpass.getuser(),
                      'Blocked on another interface')
        except GeneralException, error:
            LOGGER.error(error)


def is_detained_by_profile(identity):
    """Check that this identity is detained with a detention profile"""
    try:
        return DetentionProfile.objects.get(
            justification=identity.justification)
    except DetentionProfile.DoesNotExist:
        return None


def find_autoenable_step(identity):
    """Find and set autoenablestep"""
    event = identity.event_set.filter(
        autoenablestep__isnull=False,
        justification=identity.justification).order_by('-event_time')[0]

    if event:
        return event.autoenablestep
    else:
        return 0


def should_pursue(identity, profile):
    """Verify that this identity is inside the defined vlans for the profile"""
    LOGGER.debug('%s is %s by a profile' % (identity.mac, identity.status))
    if profile.active_on_vlans:
        if not is_inside_vlans(identity.ip, profile.active_on_vlans):
            LOGGER.info("Ip not in activeonvlans")
            return False
        else:
            LOGGER.debug("Ip in activeonvlans")
    else:
        LOGGER.debug("Profile has no activeonvlans set")

    return True


def detain(identity, candidate):
    """Detain based on identity info"""
    username = getpass.getuser()
    comment = "Detained automatically when switching ports"

    try:
        if identity.status == 'disabled':
            LOGGER.debug("Trying to disable %s" % identity.mac)
            disable(candidate, identity.justification, username, comment,
                    identity.autoenablestep)

        elif identity.status == 'quarantined':
            LOGGER.debug("Trying to quarantine %s with vlan %s"
                         % (identity.mac, identity.tovlan))
            quarantine(candidate, identity.tovlan, identity.justification,
                       username, comment, identity.autoenablestep)
    except GeneralException, error:
        LOGGER.error(error)


if __name__ == '__main__':
    main()