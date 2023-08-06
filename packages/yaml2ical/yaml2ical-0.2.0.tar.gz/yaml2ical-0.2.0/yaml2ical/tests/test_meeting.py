# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import unittest

from yaml2ical import meeting
from yaml2ical.tests import sample_data


class MeetingTestCase(unittest.TestCase):

    def test_load_yaml_file(self):
        m = meeting.load_meetings(sample_data.WEEKLY_MEETING)[0]
        self.assertEqual('OpenStack Subteam Meeting', m.project)
        self.assertEqual('Joe Developer', m.chair)
        self.assertEqual('Weekly meeting for Subteam project.\n',
                         m.description)

    def should_be_conflicting(self, yaml1, yaml2):
        """Exception is raised when meetings should conflict."""
        meeting_one = meeting.load_meetings(yaml1)
        meeting_two = meeting.load_meetings(yaml2)
        meeting_list = [meeting_one.pop(), meeting_two.pop()]
        self.assertRaises(meeting.MeetingConflictError,
                          meeting.check_for_meeting_conflicts,
                          meeting_list)

    def should_not_conflict(self, yaml1, yaml2):
        """No exception raised when meetings shouldn't conflict."""
        meeting_one = meeting.load_meetings(yaml1)
        meeting_two = meeting.load_meetings(yaml2)
        meeting_list = [meeting_one.pop(), meeting_two.pop()]
        meeting.check_for_meeting_conflicts(meeting_list)

    def test_weekly_conflict(self):
        self.should_be_conflicting(
            sample_data.WEEKLY_MEETING,
            sample_data.CONFLICTING_WEEKLY_MEETING)
        self.should_not_conflict(
            sample_data.WEEKLY_MEETING,
            sample_data.WEEKLY_OTHER_CHANNEL_MEETING)

    def test_biweekly_conflict(self):
        self.should_be_conflicting(
            sample_data.WEEKLY_MEETING,
            sample_data.ALTERNATING_MEETING)
        self.should_not_conflict(
            sample_data.ALTERNATING_MEETING,
            sample_data.BIWEEKLY_EVEN_MEETING)
        self.should_be_conflicting(
            sample_data.ALTERNATING_MEETING,
            sample_data.BIWEEKLY_ODD_MEETING)
        self.should_not_conflict(
            sample_data.BIWEEKLY_ODD_MEETING,
            sample_data.BIWEEKLY_EVEN_MEETING)
