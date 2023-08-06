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
from collections import OrderedDict
import os

from turberfield.machina.shifter import Shifter
from turberfield.utils.expert import Expert


Opportunity = namedtuple("Opportunity", ["actor", "stage", "deadline"])
Placement = namedtuple("Placement", ["actor", "stage"])


class Company(Expert):
    """
            # TODO:
            # 1. Look up collision by id
            # 2. Check timeframe acceptable
            # 3. Check actor is on stage
            # 4. Check destination valid
            # 5. Perform move to destination
    """

    @staticmethod
    def path(
        parent=os.path.expanduser(os.path.join("~", ".turberfield"))
    ):
        return os.path.join(parent, "company_input.fifo")

    @staticmethod
    def options(
        parent=os.path.expanduser(os.path.join("~", ".turberfield"))
    ):
        return OrderedDict([
            ("players", Expert.Attribute("players")),
            ("opportunity", Expert.Attribute("opportunity")),
            ("opportunities", Expert.RSON(
                "opportunities",
                "opportunity",
                os.path.join(parent, "company_opportunities.rson")
                )),
            ("company", Expert.RSON(
                "company",
                "players",
                os.path.join(parent, "company_players.rson")
                )),
        ])

    def __init__(self, positions, pockets, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._positions = positions  # Actor: Stage
        self._pockets = pockets  # Actor: (Commodity: n)

    @asyncio.coroutine
    def __call__(self, loop=None):
        while True:
            yield from Shifter.public.active.wait()
            lookup = {v.uuid: v for v in Shifter.public.movement}
            t = Shifter.public.tick.t
            ts = Shifter.public.tick.ts
            opportunities = []
            for exit in Shifter.public.collisions:

                if exit.closes < t:
                    continue

                deadline = ts + exit.closes - t
                whichever = {
                    exit.home.uuid: lookup[exit.away.uuid],
                    exit.away.uuid: lookup[exit.home.uuid]
                }
                opportunities.extend([
                    Opportunity(
                        actor,
                        whichever[stage.id],
                        deadline
                    )
                    for actor, stage in self._positions.items()
                    if stage.id in whichever])

                # TODO: Perform NPC moves (ultimately done elsewhere)

            self.declare(
                dict(
                    opportunity=opportunities,
                    players=[
                        Placement(actor, stage.id)
                        for actor, stage in self._positions.items()
                    ],
                ),
                loop=loop,
            )
            yield from Shifter.public.inactive.wait()

    @asyncio.coroutine
    def watch(self, q, **kwargs):
        loop = kwargs.pop("loop", None)
        msg = object()
        while msg is not None:
            data = yield from q.get()
            try:
                msg = Opportunity(*data)
            except TypeError:
                self._log.warning(data)
                continue

            try:
                actor = next(
                    i for i in self._positions if i.name == msg.actor
                )
            except StopIteration:
                self._log.warning(msg)
                continue

            try:
                stage = next(
                    i for i in self._positions.values()
                    if i.id == msg.stage
                )
            except StopIteration:
                self._log.warning(msg)
                continue

            self._positions[actor] = stage

            self.declare(
                dict(
                    opportunity=[],
                    players=[
                        Placement(actor, stage.id)
                        for actor, stage in self._positions.items()
                    ],
                ),
                loop=loop,
            )
