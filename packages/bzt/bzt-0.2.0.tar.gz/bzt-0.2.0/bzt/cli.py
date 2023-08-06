#! /usr/bin/env python
"""
CLI tool wrapper to run Engine using command-line interface

Copyright 2015 BlazeMeter Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from logging import Formatter, FileHandler
from optparse import OptionParser, BadOptionError, Option
import logging
import os
import platform
import sys
import tempfile
import traceback

from colorlog import ColoredFormatter

from bzt import ManualShutdown, NormalShutdown
import bzt
from bzt.engine import Engine, Configuration
from bzt.utils import run_once


class CLI(object):
    """
    'cli' means 'tool' in hebrew, did you know that?

    :param options: OptionParser parsed parameters
    """

    def __init__(self, options):
        self.signal_count = 0
        self.options = options
        self.setup_logging(options)
        self.log = logging.getLogger('')
        self.log.info("Taurus CLI Tool v%s", bzt.version)
        logging.debug("Command-line options: %s", self.options)
        self.engine = Engine(self.log)
        self.engine.artifacts_base_dir = self.options.datadir
        self.engine.file_search_path = os.getcwd()

    @staticmethod
    @run_once
    def setup_logging(options):
        """
        Setting up console and file loggind, colored if possible

        :param options: OptionParser parsed options
        """
        colors = {
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
        fmt_file = Formatter("[%(asctime)s %(levelname)s %(name)s] %(message)s")
        if sys.stdout.isatty():
            fmt_verbose = ColoredFormatter("%(log_color)s[%(asctime)s %(levelname)s %(name)s] %(message)s",
                                           log_colors=colors)
            fmt_regular = ColoredFormatter("%(log_color)s%(asctime)s %(levelname)s: %(message)s",
                                           "%H:%M:%S", log_colors=colors)
        else:
            fmt_verbose = Formatter("[%(asctime)s %(levelname)s %(name)s] %(message)s")
            fmt_regular = Formatter("%(asctime)s %(levelname)s: %(message)s", "%H:%M:%S")

        logger = logging.getLogger('')
        logger.setLevel(logging.DEBUG)

        # log everything to file
        if options.log:
            file_handler = logging.FileHandler(options.log)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(fmt_file)
            logger.addHandler(file_handler)

        # log something to console
        console_handler = logging.StreamHandler(sys.stdout)

        if options.verbose:
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(fmt_verbose)
        elif options.quiet:
            console_handler.setLevel(logging.WARNING)
            console_handler.setFormatter(fmt_regular)
        else:
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(fmt_regular)

        logger.addHandler(console_handler)

    def perform(self, configs):
        """
        Run the tool

        :type configs: list
        :return: integer exit code
        """
        overrides = []
        jmx_shorthands = []
        try:
            jmx_shorthands = self.__get_jmx_shorthands(configs)
            configs.extend(jmx_shorthands)

            overrides = self.__get_config_overrides()
            configs.extend(overrides)

            logging.info("Starting with configs: %s", configs)
            self.engine.configure(configs)

            # apply aliases
            for alias in self.options.aliases:
                al_config = self.engine.config.get("cli-aliases").get(alias, None)
                if al_config is None:
                    raise RuntimeError("Alias '%s' is not found within configuration" % alias)
                self.engine.config.merge(al_config)

            self.engine.prepare()
            self.engine.run()
            exit_code = 0
        except BaseException as exc:
            self.log.debug("Caught exception in try: %s", traceback.format_exc())
            if isinstance(exc, ManualShutdown):
                self.log.info("Interrupted by user: %s", exc)
            elif isinstance(exc, NormalShutdown):
                self.log.info("Normal shutdown")
            else:
                self.log.error("Exception: %s", exc)
            self.log.warning("Please wait for graceful shutdown...")
            exit_code = 1
        finally:
            try:
                for fname in overrides + jmx_shorthands:
                    os.remove(fname)
                self.engine.post_process()
            except BaseException as exc:
                self.log.debug("Caught exception in finally: %s", traceback.format_exc())
                self.log.error("Exception: %s", exc)
                exit_code = 1

        self.log.info("Artifacts dir: %s", self.engine.artifacts_dir)
        self.log.info("Done performing with code: %s", exit_code)
        if self.options.log:
            if platform.system() == 'Windows':
                # need to finalize the logger before moving file
                for handler in self.log.handlers:
                    if isinstance(handler, FileHandler):
                        self.log.debug("Closing log handler: %s", handler.baseFilename)
                        handler.close()
                self.engine.existing_artifact(self.options.log)
                # os.remove(self.options.log) does not work - says that file is busy
            else:
                self.engine.existing_artifact(self.options.log, True)
        return exit_code

    def __get_config_overrides(self):
        if self.options.option:
            self.log.debug("Adding overrides: %s", self.options.option)
            fds, fname = tempfile.mkstemp(".ini", "overrides_", dir=self.engine.artifacts_base_dir)
            os.close(fds)
            with open(fname, 'w') as fds:
                fds.write("[DEFAULT]\n")
                for option in self.options.option:
                    fds.write(option + "\n")
            return [fname]
        else:
            return []

    def __get_jmx_shorthands(self, configs):
        jmxes = []
        for n, filename in enumerate(configs):
            if filename.lower().endswith(".jmx"):
                jmxes.append(configs.pop(n))

        if jmxes:
            self.log.debug("Adding JMX shorthand config for: %s", jmxes)
            fds, fname = tempfile.mkstemp(".json", "jmxes_", dir=self.engine.artifacts_base_dir)
            os.close(fds)

            config = Configuration()

            for jmx_file in jmxes:
                config.get("execution", []).append({"executor": "jmeter", "scenario": {"script": jmx_file}})

            config.dump(fname, Configuration.JSON)

            return [fname]
        else:
            return []


class OptionParserWithAliases(OptionParser, object):
    """
    Decorator that processes short opts as aliases
    """

    def __init__(self,
                 usage=None,
                 option_list=None,
                 option_class=Option,
                 version=None,
                 conflict_handler="error",
                 description=None,
                 formatter=None,
                 add_help_option=True,
                 prog=None,
                 epilog=None):
        super(OptionParserWithAliases, self).__init__(
            usage=usage, option_list=option_list,
            option_class=option_class, version=version,
            conflict_handler=conflict_handler, description=description, formatter=formatter,
            add_help_option=add_help_option, prog=prog, epilog=epilog)
        self.aliases = []

    def _process_short_opts(self, rargs, values):
        if rargs:
            candidate = rargs[0]
        else:
            candidate = None
        # sys.stderr.write("Rargs: %s\n" % rargs)
        try:
            return OptionParser._process_short_opts(self, rargs, values)
        except BadOptionError as exc:
            if candidate.startswith(exc.opt_str) and len(candidate) > 2:
                self.aliases.append(candidate[1:])
            else:
                raise
            pass

    def parse_args(self, args=None, values=None):
        res = OptionParser.parse_args(self, args, values)
        res[0].aliases = self.aliases
        return res


def main():
    """
    This function is used as entrypoint by setuptools
    """
    usage = "Usage: bzt [options] [configs] [-aliases]"
    dsc = "BlazeMeter Taurus Tool v%s, the configuration-driven test running engine" % bzt.version
    parser = OptionParserWithAliases(usage=usage, description=dsc, prog="bzt")
    parser.add_option('-d', '--datadir', action='store', default=".",
                      help="Artifacts base dir")
    parser.add_option('-l', '--log', action='store', default="bzt.log",
                      help="Log file location")
    parser.add_option('-o', '--option', action='append',
                      help="Override option in config")
    parser.add_option('-q', '--quiet', action='store_true',
                      help="Only errors and warnings printed to console")
    parser.add_option('-v', '--verbose', action='store_true',
                      help="Prints all logging messages to console")

    parsed_options, parsed_configs = parser.parse_args()

    executor = CLI(parsed_options)

    try:
        code = executor.perform(parsed_configs)
    except BaseException as exc_top:
        logging.error("Exception: %s", exc_top)
        logging.debug("Exception: %s", traceback.format_exc())
        code = 1

    exit(code)


if __name__ == "__main__":
    main()
