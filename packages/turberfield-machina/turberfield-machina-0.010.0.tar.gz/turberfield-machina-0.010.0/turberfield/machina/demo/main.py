#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

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


import argparse
import concurrent.futures
import datetime
from decimal import Decimal as Dl
import json
import logging
from logging.handlers import WatchedFileHandler
import operator
import os
import os.path
import sys
import time

import bottle
from bottle import Bottle
import pkg_resources

from turberfield.machina import __version__
from turberfield.machina.company import Company
from turberfield.machina.company import Opportunity
from turberfield.machina.company import Placement

import turberfield.machina.demo.elements
from turberfield.machina.demo.elements import Action
from turberfield.machina.demo.elements import Parameter
import turberfield.machina.demo.simulation

from turberfield.machina.utils import rson2objs

from turberfield.utils.expert import TypesEncoder
from turberfield.utils.pipes import SimplePipeQueue


DFLT_LOCN = os.path.expanduser(os.path.join("~", ".turberfield"))

__doc__ = """
Serves a graphical web interface for Turberfield machina.
"""

bottle.TEMPLATE_PATH.append(
    pkg_resources.resource_filename(
        "turberfield.machina.demo", "templates"
    )
)

app = Bottle()


@app.route("/", "GET")
@bottle.view("simulation")
def simulation_get():
    log = logging.getLogger("turberfield.machina.demo.home")
    path = os.path.join(
        app.config["args"].output, "company_players.rson"
    )

    user = "some.body@gmail.com"
    rv = {
        "info": {
            "args": app.config.get("args"),
            "debug": bottle.debug,
            "actor": None,
            "interval": 200,
            "location": None,
            "refresh": None,
            "time": "{:.1f}".format(time.time()),
            "title": "Turberfield machina {}".format(__version__),
            "version": __version__
        },
        "items": [
        ],
        "options": [
            turberfield.machina.demo.elements.login()
        ]
    }
    try:
        with open(path, 'r') as content:
            data = rson2objs(content.read(), types=(Placement,))
            placement = next(i for i in data if i.actor[2] == user)
            rv["info"]["actor"] = placement.actor[0]
            stage = app.config["sites"][placement.stage]
            actors = [
                i.actor for i in data
                if i.stage == placement.stage
            ]
            actors.remove(placement.actor)
            rv["info"]["location"] = stage.label
            rv["items"].extend(actors)
    except Exception as e:
        log.exception(e)
    finally:
        return rv


@app.route("/events/<actor>", "GET")
def events_get(actor):
    log = logging.getLogger("turberfield.machina.demo.events")
    sites = app.config.get("sites")
    path = os.path.join(
        app.config["args"].output, "company_opportunities.rson"
    )
    ts = time.time()
    page = {
        "info": {
            "actor": actor,
            "interval": 200,
            "refresh": None,
            "time": "{:.1f}".format(ts),
            "title": "Turberfield machina {}".format(__version__),
            "version": __version__
        },
        "nav": [],
        "items": [],
        "options": [],
    }
    try:
        with open(path, 'r') as content:
            data = rson2objs(content.read(), types=(Opportunity,))
            page["items"] = [dict(
                label=i.stage[1],
                uuid=i.stage[0], closes=i.deadline,
                _links=[
                    vars(Action(
                        "Quick! {:.0f}s".format(i.deadline - ts),
                        "canonical", "/stage/{}", i.stage[0], "post",
                        [Parameter("actor", True, "", [actor], "")],
                        "Go")),
                ]
                ) for i in data
                if i.actor[0] == actor and i.deadline > ts
            ]
    except Exception as e:
        log.exception(e)
    finally:
        return json.dumps(
            page, cls=TypesEncoder, indent=4
        )


@app.route("/stage/<uuid>", method="POST")
def stage_post(uuid):
    log = logging.getLogger("turberfield.machina.demo.stage")
    actor = bottle.request.forms.get("actor")
    path = Company.path(app.config["args"].output)
    msg = Opportunity(actor, uuid, time.time())
    pq = SimplePipeQueue.pipequeue(path)
    pq.put_nowait(tuple(msg))
    pq.close()
    bottle.redirect("/")


@app.route("/css/<filename>")
def serve_css(filename):
    locn = pkg_resources.resource_filename(
        "turberfield.machina.demo", "static/css")
    return bottle.static_file(filename, root=locn)


@app.route("/js/<filename>")
def serve_js(filename):
    locn = pkg_resources.resource_filename(
        "turberfield.machina.demo", "static/js")
    return bottle.static_file(filename, root=locn)


@app.route("/data/<filename>")
def serve_data(filename):
    bottle.request.environ["HTTP_IF_MODIFIED_SINCE"] = None
    locn = app.config["args"].output
    response = bottle.static_file(filename, root=locn)
    response.expires = os.path.getmtime(locn)
    response.set_header("Cache-control", "max-age=0")
    return response


def main(args):
    log = logging.getLogger("turberfield.machina.demo")
    log.setLevel(args.log_level)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-7s %(name)s|%(message)s")
    ch = logging.StreamHandler()

    if args.log_path is None:
        ch.setLevel(args.log_level)
    else:
        fh = WatchedFileHandler(args.log_path)
        fh.setLevel(args.log_level)
        fh.setFormatter(formatter)
        log.addHandler(fh)
        ch.setLevel(logging.WARNING)

    ch.setFormatter(formatter)
    log.addHandler(ch)

    bottle.debug(True)
    bottle.TEMPLATES.clear()

    sites = {
        entry[0].uuid: entry[0] for struct in (
            turberfield.machina.demo.simulation.Simulation.patterns,
            turberfield.machina.demo.simulation.Simulation.static)
        for entry in struct}

    with concurrent.futures.ProcessPoolExecutor() as executor:
        future = executor.submit(
            turberfield.machina.demo.simulation.run,
        )
        app.config.update({
            "args": args,
            "jobs": set([future]),
            "sites": sites,
        })
        bottle.run(app, host="localhost", port=8080)


def parser(descr=__doc__):
    rv = argparse.ArgumentParser(description=descr)
    rv.add_argument(
        "--version", action="store_true", default=False,
        help="Print the current version number")
    rv.add_argument(
        "-v", "--verbose", required=False,
        action="store_const", dest="log_level",
        const=logging.DEBUG, default=logging.INFO,
        help="Increase the verbosity of output")
    rv.add_argument(
        "--log", default=None, dest="log_path",
        help="Set a file path for log output")
    rv.add_argument(
        "--output", default=DFLT_LOCN,
        help="path to output directory [{}]".format(DFLT_LOCN))
    return rv


def run():
    p = parser()
    args = p.parse_args()
    if args.version:
        sys.stdout.write(__version__ + "\n")
        rv = 0
    else:
        try:
            os.mkdir(args.output)
        except OSError:
            pass
        rv = main(args)
    sys.exit(rv)

if __name__ == "__main__":
    run()
