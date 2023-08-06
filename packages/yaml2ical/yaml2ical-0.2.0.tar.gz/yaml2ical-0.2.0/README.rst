=========
yaml2ical
=========

This tool converts a series of meeting descriptions in YAML format into one
or several .ics files suitable for calendaring. It checks for scheduling
conflicts in specific locations.

Rationale
=========

yaml2ical aims to provide an easier way to manage OpenStack team meetings.
Currently, each team's meeting time and agenda are listed at:

  https://wiki.openstack.org/wiki/Meetings

This project allows to replace each meeting with well-defined YAML files,
which can be code-reviewed, then continuously-integrated into .ics files for
general consumption.

Getting Started
===============

Running Locally from Command Line
---------------------------------

To test this project locally, you must have the following requirements
installed:

* Python 3.3+
* `iCalendar` python library
* `PyYaml` python library

Before running this tool, first edit some meeting YAML files in the meetings
directory. To create a new meeting YAML file, read the `YAML Meeting File`
section below.

  ::

    $ pip install yaml2ical
    $ yaml2ical
    usage: yaml2ical [-h] -y YAML_DIR -i ICAL_DIR [-f]

    A tool that automates the process for testing, integrating, and
    publishing changes to OpenStack meetings using the existing OpenStack
    project infrastructure.

    optional arguments:
      -h, --help            show this help message and exit
      -y YAML_DIR, --yamldir YAML_DIR
                            directory containing YAML to process
      -i ICAL_DIR, --icaldir ICAL_DIR
                          directory to store converted iCal
      -f, --force           forcefully remove old .ics files from iCal
      directory


The following are a few scenarios:

Generate .ics files locally from existing yaml meeting files:

  ::

    $ yaml2ical -y meetings/ -i icals/

The generated .ics files are not tracked in this git repository,
but they are available locally to import into your calendar. Note,
to remove stale .ics files, use the ``--force`` argument:

  ::

    $ ls icals/
    Barbican Meeting-b58d78a4.ics
    Ceilometer Team Meeting-9ed7b5b4.ics
    Chef Cookbook Meeting-2418b331.ics

With each .ics file looking something similar to:

  ::

    $ cat icals/Barbican\ Meeting-b58d78a4.ics
    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//yaml2ical agendas//EN
    BEGIN:VEVENT
    SUMMARY:Barbican Meeting (openstack-meeting-alt)
    DTSTART;VALUE=DATE-TIME:20141006T200000Z
    DURATION:PT1H
    DESCRIPTION:Project:  Barbican Meeting\nChair:  jraim\nIRC:  openstack-meet
     ing-alt\nAgenda:'* malini - update on Security Guide documentation\n\n  *
     alee_/atiwari - Crypto plugin changes\n\n  * arunkant - Target support in
     barbican policy enforcement\n\n  * jaraim - Support for debug mode start i
     n barbican\, can be merged?\n\n  '\n\nDescription:  The Barbican project t
     eam holds a weekly team meeting in\n#openstack-meeting-alt:\n* Weekly on M
     ondays at 2000 UTC\n* The blueprints that are used as a basis for the Barb
     ican project can be\n  found at https://blueprints.launchpad.net/barbican\
     n* Notes for previous meetings can be found here.\n* Chair (to contact for
      more information): jraim (#openstack-barbican @\n  Freenode)\n
    RRULE:FREQ=WEEKLY
    END:VEVENT
    END:VCALENDAR


YAML Meeting File
=================

Each meeting consists of:

* ``project``: the name of the project
* ``schedule``: a list of schedule each consisting of

  * ``time``: time string in UTC
  * ``day``: the day of week the meeting takes place
  * ``irc``: the irc room in which the meeting is held
  * ``frequency``: frequent occurrence of the meeting
* ``chair``: name of the meeting's chair
* ``description``: a paragraph description about the meeting

The file name should be a lower-cased, hyphenated version of the meeting name,
ending with ``.yaml`` . For example, ``Keystone team meeting`` should be
saved under ``keystone-team-meeting.yaml``.

Example
-------

This is an example for the yaml meeting for Nova team meeting.  The whole file
will be import into Python as a dictionary.

* The project name is shown below.

  ::

    project:  Nova Team Meeting

* The schedule is a list of dictionaries each consisting of `time` in UTC,
  `day` of the week, the `irc` meeting room, and the `frequency` of the
  meeting. Options for the `frequency` are `weekly`, `biweekly-even`, and
  `biweekly-odd` at the moment.

  ::

    schedule:
        - time:       '1400'
          day:        Thursday
          irc:        openstack-meeting-alt
          frequency:  biweekly-even

        - time:       '2100'
          day:        Thursday
          irc:        openstack-meeting
          frequency:  biweekly-odd

* The chair is just a one liner. The might be left empty if there is not a
  chair.

  ::

    chair:  Russell Bryant

* The project description is as follows.  Use `>` for paragraphs where new
  lines are folded, or `|` for paragraphs where new lines are preserved.

  ::

    description:  >
        This meeting is a weekly gathering of developers working on OpenStack.
        Compute (Nova). We cover topics such as release planning and status,
        bugs, reviews, and other current topics worthy of real-time discussion.
