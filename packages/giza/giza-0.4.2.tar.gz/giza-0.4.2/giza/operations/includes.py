# Copyright 2014 MongoDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Entry points to view data generated by ``giza.includes`` code. These functions
make it possible to introspect the implicit relationship between source files
and detect unused includes or includes that are only used once, as well as
nested includes.
"""


import os
import logging
import json

import argh

logger = logging.getLogger('giza.operations.includes')

from giza.core.app import BuildApp
from giza.config.helper import fetch_config

from giza.includes import (included_once, included_recusively,
                           includes_masked, include_files,
                           include_files_unused, changed_includes)

## Helper

def render_for_console(data):
    print(json.dumps(data, indent=3))

## Entry Points

@argh.expects_obj
def recursive(args):
    c = fetch_config(args)

    render_for_console(included_recusively(conf=c))

@argh.expects_obj
def changed(args):
    c = fetch_config(args)

    render_for_console(changed_includes(conf=c))

@argh.expects_obj
def once(args):
    c = fetch_config(args)

    render_for_console(included_once(conf=c))

@argh.expects_obj
def unused(args):
    c = fetch_config(args)

    render_for_console(include_files_unused(conf=c))

@argh.expects_obj
def list(args):
    c = fetch_config(args)

    render_for_console(include_files(conf=c).keys())

@argh.arg('--filter', '-f', default=None, dest="include_mask")
@argh.expects_obj
def graph(args):
    c = fetch_config(args)

    if c.runstate.include_mask is None:
        render_for_console(include_files(conf=c))
    else:
        if c.runstate.include_mask.startswith(c.paths.source):
            mask = mask[6:]
        elif c.runstate.include_mask.startswith('/' + c.paths.source):
            mask = mask[7:]
        else:
            mask = c.runstate.include_mask

        render_for_console(includes_masked(mask=mask, conf=c))

@argh.expects_obj
def clean(args):
    c = fetch_config(args)

    for fn in include_files_unused(conf=c):
        fn = os.path.join(conf.paths.source, fn[1:])
        if os.path.exists(fn):
            os.remove(fn)
            logger.info("removed {0}, which was an unused include file.".format(fn))
        else:
            logger.error('{0} does not exist'.format(fn))
