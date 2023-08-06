# repov <https://github.com/msikma/repov>
# Copyright (C) 2015, Michiel Sikma <michiel@sikma.org>
# MIT licensed

import subprocess
import re
import os


class Parser(object):
    # The active Git command.
    git_cmd = 'git'

    # The argument recipes we can pass to Git to get version information.
    git_args = {}

    # Helper regex for parsing segments.
    # Parses everything in between % characters, but permits escaping \%.
    tpl_re = r'%([^%]*?(\\\%)?[^%]*?[^\\])%'

    # The substitute in case we can't parse or understand a segment.
    unknown_segment = '(unknown)'

    def parse_segments_from_template(self, tpl):
        '''
        Extracts segments from a template string, runs Git commands to retrieve
        their results where possible, and then returns them as an object.
        '''
        parsed_segments = {}

        # Iterate over every segment in the template and run its
        # corresponding Git command.
        template_segments = self.parse_template(tpl)
        for segment in template_segments:
            segment_cmd = self.git_args[segment]

            # Attempt to run the command. If it fails, set the segment to
#           # the unknown segment string.
            try:
                parsed_segments[segment] = self.parse_segment(segment_cmd)
                cmd_success = True
            except:
                parsed_segments[segment] = Parser.unknown_segment
                cmd_success = False

            # If we have a transformer function, call it on the output
            # before returning it, even if the command failed.
            # Can't do `if segment_cmd[1]:` like in the Javascript.
            if len(segment_cmd) >= 2:
                parsed_segments[segment] = segment_cmd[1](
                    parsed_segments[segment], cmd_success
                )

        return parsed_segments


    def parse_template(self, tpl):
        '''
        Returns an array of replaceable segments extracted from the template.
        '''
        return [match[0] for match in re.findall(Parser.tpl_re, tpl)]

    def parse_segment(self, segment_cmd):
        '''
        Runs a synchronous console command for a segment and returns the
        result. If a transformer function is defined, the output is first
        passed through it before it's returned.

        This uses /dev/null to pipe error output in case something is wrong.
        '''
        with open(os.devnull, 'w') as devnull:
            return subprocess.check_output(
                Parser.git_cmd + ' ' + segment_cmd[0],
                shell=True, stderr=devnull
            ).strip()


    def decorate_template(self, tpl, segments):
        '''
        Takes a template and an object of the parsed segments from that
        template, and returns a neatly decorated version string.
        '''
        for segment in segments:
            # Replace the %original% string from the template with
            # the {original: 'something'} that was retrieved from Git.
            tpl = str.replace(tpl, '%' + segment + '%', segments[segment])

        return tpl

    def set_git_args(self, args):
        '''
        Sets the current list of active Git arguments.
        '''
        Parser.git_args = args
        return True

    def merge_git_args(self, args):
        '''
        Merges together a set of Git arguments with the current ones.
        '''
        for arg in args:
            Parser.git_args[arg] = args[arg]
        return True
