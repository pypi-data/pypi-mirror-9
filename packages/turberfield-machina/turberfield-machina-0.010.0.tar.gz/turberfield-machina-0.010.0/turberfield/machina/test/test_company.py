#!/usr/bin/env python3
# encoding: UTF-8

# This file is part of turberfield.
#
# Turberfield is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Turberfield is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with turberfield.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
from collections import namedtuple
import unittest
import warnings

from turberfield.machina.company import Company
from turberfield.machina.stage import Stage
from turberfield.machina.test.test_shifter import ShifterTests

# Prototyping
from collections import Counter
from collections import defaultdict
from collections import namedtuple
import random
import uuid
Character = namedtuple("Character", ["name", "uuid", "luck"])

__doc__ = """
.. todo:: Test Placement and Opportunity.
"""


class CompanyTest(unittest.TestCase):

    def create_cast():
        rv = OrderedDict([
            (stage, Mobile(
                steadypace(trajectory(), routing, timing), 10))
            for stage, routing, timing in Simulation.patterns])
        rv.update(
            OrderedDict([
                (stage, Fixed(posn, reach))
                for stage, posn, reach in Simulation.static]))
        return rv

    def setUp(self):
        class_ = self.__class__
        class_.theatre = ShifterTests.create_theatre()

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        warnings.simplefilter("ignore")

        self._options = dict(players=Company.options()["players"])

    def test_populate(self):
        npcs = [
            Character(i, uuid.uuid4().hex, random.random())
            for i in ["Alice", "Bob", "Charlie"]]
        positions = {
            p: random.choice(
                [Stage(i.uuid) for i in CompanyTest.theatre]
            ) for p in npcs}
        pockets = defaultdict(Counter)

        company = Company(
            positions, pockets, loop=self.loop, **self._options
        )
        self.fail(company)

    def test_communicate(self):
        q = asyncio.Queue(loop=self.loop)
        self.assertTrue(q.empty())
        self.loop.run_until_complete(
            asyncio.wait_for(q.put("Boo"), 2, loop=self.loop))
        self.assertFalse(q.empty())

        company = Company({}, {}, q, loop=self.loop, **self._options)
        self.loop.run_until_complete(asyncio.wait(
            asyncio.Task.all_tasks(loop=self.loop),
            timeout=2, loop=self.loop
        ))
        self.assertTrue(q.empty())
        print(Company.public.players)
