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
:mod:`giza.operations.make` provides an alternate method for running build
operations, by specifying operations as a list of strings that resemble ``make``
targets. These targets are compatible with the targets created in the default
``sphinx-quickstart`` ``makefile``, and also supports a number of additional
options for specifying "editions" and human-language variants of build
operations, as well as deployment ("push") and packaging operations.

Many projects retain a default makefile that passes all make operations through
to this mode of giza operation, with the following target:

.. code-block:: makefile

   %:
       giza make %@
"""

import logging
import copy
import argh

from giza.core.app import BuildApp
from giza.config.helper import fetch_config
from giza.config.sphinx_config import avalible_sphinx_builders
from giza.operations.deploy import deploy_tasks
from giza.operations.sphinx_cmds import sphinx_publication
from giza.operations.build_env import env_package_worker
from giza.tools.serialization import dict_from_list
from giza.tools.strings import hyph_concat

logger = logging.getLogger('giza.operations.make')

def derive_command(name, conf):
    """
    :param str name: The name of a build operation. Currently supports
        ``sphinx``, ``env``, ``deploy``. Unknown operations are ignored.

    :param Configuration conf: The top level configuration object.

    Given a ``conf`` object and the name of the operation, logs a message with a
    complete specific giza command that describes an equivalent specific command.
    """

    if name in ('sphinx', 'env'):
        cmd = ["giza", name]

        if conf.runstate.serial_sphinx is True:
            cmd.append('--serial_sphinx')

        if len(conf.runstate.builder) > 0:
            cmd.append('--builder')
            cmd.append(' '.join(conf.runstate.builder))

        if len(conf.runstate.editions_to_build) > 0 and conf.runstate.editions_to_build[0] is not None:
            cmd.append('--edition')
            cmd.append(' '.join(conf.runstate.editions_to_build))

        if len(conf.runstate.languages_to_build) > 0 and conf.runstate.languages_to_build[0] is not None:
            cmd.append('--language')
            cmd.append(' '.join(conf.runstate.languages_to_build))

        if name == 'sphinx':
            logger.info('running sphinx build operation, equivalent to: ' + ' '.join(cmd))
        elif name == 'env':
            logger.info('running env cache operation, equivalent to: ' + ' '.join(cmd))
    elif name == 'deploy':
        cmd = ["giza deploy"]
        cmd.append('--target')
        cmd.append(' '.join(conf.runstate.push_targets))

        logger.info('running deploy operation, equivalent to: ' + ' '.join(cmd))

def add_sphinx_build_options(action_spec, action, options, conf):
    """
    :param dict action_spec: A reference to a dictionary that defines a

    Modifies the ``action_spec`` document to define a build operation with the
    appropriate options, based on the operation (``action``) and the
    ``options``.

    If the options do not specify one or more editions in a project that uses
    editions, will add all configured editions to the build operation.
    """

    sphinx_builders = avalible_sphinx_builders()

    if action in sphinx_builders:
        action_spec['builders'].add(action)

    for build_option in options:
        if build_option in sphinx_builders:
            action_spec['builders'].add(build_option)
        elif build_option in conf.project.edition_list:
            action_spec['editions'].add(build_option)
        elif build_option in conf.system.files.data.integration:
            action_spec['languages'].add(build_option)

    if 'editions' in conf.project and len(action_spec['editions']) == 0:
        action_spec['editions'].update(conf.project.edition_list)

@argh.arg('make_target', nargs="*")
@argh.arg('--serial_sphinx', action='store_true')
@argh.named('make')
@argh.expects_obj
def main(args):
    """
    Provides a way to specify make-like targets to invoke giza
    operations. Targets take a <action>-<option<-option>> form.
    """
    targets = [ (t[0], t[1:]) for t in [ t.split("-") for t in args.make_target ] ]

    conf = fetch_config(args)

    run_make_operations(targets, conf)

def run_make_operations(targets, conf):
    """
    :param list targets: A list of tuples in the form of ``(<action>, [option,
         option])`` that define build targets.

    :param Configuration conf: The top level configuration object.

    Parses the ``targets`` list and runs tasks defined, including all specified
    sphinx targets, all ``push`` deployment targets, and will create the ``env``
    packages. Noteworthy behavior:

    - The order of options *except* for the action in the first option is not
      important.

    - If you run ``push`` target with the ``deploy`` option
      (i.e. ``push-deploy`` or ``push-<edition>-deploy``), ``giza`` will *not*
      run the ``publish`` Sphinx build.

    - This interface assumes that all deployment targets (defined in each
      project begin with ``push-`` or ``stage-``.) If you have a project with
      different deployment targets, you will need to call ``giza deploy``
      directly.

    - The ``env`` cache targets take the same options as the Sphinx builders and
      package the environment for only those builders. If you specify ``env``
      after a Sphinx target, ``giza`` will build the cache for only that
      package.
    """

    sphinx_opts = { "worker": sphinx_publication,
                    "languages": set(),
                    "editions": set(),
                    "builders": set() }
    push_opts = { "worker": deploy_tasks,
                  "targets": set() }
    packaging_opts = { }

    sphinx_builders = avalible_sphinx_builders()
    deploy_configs = dict_from_list('target', conf.system.files.data.push)

    tasks = []
    for action, options in targets:
        if action in sphinx_builders:
            tasks.append(sphinx_opts)

            add_sphinx_build_options(sphinx_opts, action, options, conf)
        elif action in ('stage', 'push'):
            tasks.append(push_opts)

            if 'deploy' not in options:
                sphinx_opts['builders'].add('publish')
                tasks.append(sphinx_opts)
                add_sphinx_build_options(sphinx_opts, action, options, conf)

            for build_option in options:
                deploy_target_name = hyph_concat(action, build_option)
                if deploy_target_name in deploy_configs:
                    push_opts['targets'].add(deploy_target_name)
        elif action.startswith('env'):
            if len(packaging_opts) > 0:
                packaging_opts = copy.copy(sphinx_opts)
                packaging_opts['worker'] = env_package_worker

            tasks.append(packaging_opts)
            add_sphinx_build_options(packaging_opts, False, options, conf)
        else:
            logger.error('target: {0} not defined in the make interface'.format(action))

    with BuildApp.context(conf) as app:
        if sphinx_opts in tasks:
            conf.runstate.languages_to_build = list(sphinx_opts['languages'])
            conf.runstate.editions_to_build = list(sphinx_opts['editions'])
            conf.runstate.builder = list(sphinx_opts['builders'])

            derive_command('sphinx', conf)

            sphinx_opts['worker'](conf, conf.runstate, app)

        if push_opts in tasks:
            conf.runstate.push_targets = list(push_opts['targets'])
            push_opts['worker'](conf, app)

            derive_command('deploy', conf)

        if packaging_opts in tasks:
            derive_command('env', conf)

            task = app.add('task')
            task.job = env_package_worker
            task.args = (conf.runstate, conf)
            task.target = False
            task.dependency = False
