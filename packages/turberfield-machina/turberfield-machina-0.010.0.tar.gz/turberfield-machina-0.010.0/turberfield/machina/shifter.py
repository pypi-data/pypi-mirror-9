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
from collections import defaultdict
from collections import namedtuple
from collections import OrderedDict
import decimal
import logging
from operator import attrgetter
import os.path
import time
import warnings


from turberfield.utils.expert import Expert
from turberfield.utils.homogeneous import vector
from turberfield.utils.travel import Impulse


__doc__ = """
Shifter moves stages around
"""

Fixed = namedtuple("Fixed", ["posn", "reach"])
Mobile = namedtuple("Mobile", ["motion", "reach"])
Tick = namedtuple("Tick", ["ts", "start", "stop", "step", "t"])

Exit = namedtuple("Exit", ["home", "away", "closes"])
Visible = namedtuple("Visible", ["uuid", "label", "symbol", "pos"])


def steadypace(integrator, routing, timing, tol=1):
    log = logging.getLogger("turberfield.positions.travel.steadypace")
    accn = vector(0, 0, 0)
    integrator.send(None)
    tBegin = yield None
    tEnd = yield None
    origin, destn = next(routing)
    tTransit = next(timing)
    imp = integrator.send(Impulse(tBegin, tEnd, accn, origin))
    hop = (destn - origin) * decimal.Decimal(tEnd - tBegin) / tTransit
    tBegin, tEnd = tEnd, (yield imp)
    imp = integrator.send(Impulse(tBegin, tEnd, accn, origin + hop))
    while True:
        tBegin, tEnd = tEnd, (yield imp)
        dist = (destn - imp.pos).magnitude
        if dist < tol:
            origin, destn = next(routing)
            tTransit = next(timing)
            hop = (destn - origin) * (tEnd - tBegin) / tTransit
            imp = integrator.send(
                Impulse(tBegin, tEnd, accn, origin + hop)
            )
        else:
            imp = integrator.send(
                Impulse(tBegin, tEnd, accn, imp.pos)
            )


class Shifter(Expert):

    @staticmethod
    def collision(theatre, pending=None):
        pending = defaultdict(int) if pending is None else pending
        while True:
            stage, impulse, expires = (yield pending)
            gaps = [
                (other, (impulse.pos - fix.posn).magnitude, fix.reach)
                for other, fix in theatre.items()
                if isinstance(fix, Fixed) and stage is not other]

            for other, gap, rad in gaps:
                if gap < rad:
                    pending[frozenset((stage, other))] = expires

    @staticmethod
    def movement(theatre, start, t):
        infinity = decimal.Decimal("Infinity")
        for stage, job in theatre.items():
            if isinstance(job, Fixed):
                imp = Impulse(
                    start, infinity, vector(0, 0, 0), job.posn
                )
                yield (stage, imp)
            elif isinstance(job, Mobile):
                if t == start:
                    job.motion.send(None)
                imp = job.motion.send(t)
                if imp is not None:
                    yield (stage, imp)

    @staticmethod
    def options(
        parent=os.path.expanduser(os.path.join("~", ".turberfield"))
    ):
        return OrderedDict([
            ("active", Expert.Event("active")),
            ("inactive", Expert.Event("inactive")),
            ("tick", Expert.Attribute("tick")),
            ("collisions", Expert.Attribute("collisions")),
            ("movement", Expert.Attribute("movement")),
            ("bridging", Expert.RSON(
                "bridging",
                "collisions",
                os.path.join(parent, "shifter_bridging.rson")
            )),
            ("positions", Expert.HATEOAS(
                "positions",
                "movement",
                os.path.join(parent, "positions.json")
            )),
        ])

    def __init__(self, theatre, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.theatre = theatre
        self._detector = Shifter.collision(theatre)

    @asyncio.coroutine
    def __call__(self, start, stop, step, loop=None):
        memo = 0
        t = start
        bridging = {}
        self._detector.send(None)
        while stop > t:
            movement = []
            for stage, push in Shifter.movement(
                self.theatre, start, t
            ):
                movement.append(
                    Visible(
                        stage.uuid, stage.label,
                        stage.symbol, push.pos[0:2]
                    )
                )
                bridging = self._detector.send((stage, push, t + 5))

            collisions = [
                Exit(a, b, expires)
                for (a, b), expires in bridging.items()
            ]

            latest = sum(bridging.values())
            active = (t == start or (latest - memo) > 1)
            tick = Tick(time.time(), start, stop, step, t)
            self._log.debug(
                "Active ({}) at {}, {}".format(active, tick.ts, t)
            )
            self.declare(
                dict(
                    active=active,
                    inactive=not active,
                    collisions=collisions,
                    movement=movement,
                    tick=tick
                ),
                loop=loop,
            )

            t += step
            memo = latest
            yield from asyncio.sleep(max(step, 0.2), loop=loop)

        return tick
