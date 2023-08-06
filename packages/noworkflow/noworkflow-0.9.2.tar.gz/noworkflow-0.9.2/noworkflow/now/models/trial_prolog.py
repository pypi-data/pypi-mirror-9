# Copyright (c) 2015 Universidade Federal Fluminense (UFF)
# Copyright (c) 2015 Polytechnic Institute of New York University.
# This file is part of noWorkflow.
# Please, consult the license terms in the LICENSE file.

from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

import textwrap

from datetime import datetime

from ..utils import resource


RULES = '../resources/rules.pl'


def timestamp(string):
    epoch = datetime(1970,1,1)
    time = datetime.strptime(string, '%Y-%m-%d %H:%M:%S.%f')
    return (time - epoch).total_seconds()


class TrialProlog(object):

    prolog_cli = None

    def __init__(self, trial):
        self.trial = trial
        self.id = trial.id

    def export_trial_activations(self, result, with_doc=True):
        if with_doc:
            result.append(textwrap.dedent("""\
                %
                % FACT: activation(trial_id, id, name, start, finish, caller_activation_id).
                %
                """))
        result.append(":- dynamic(activation/6).")
        for activation in self.trial.activations():
            activation = dict(activation)
            activation['name'] = str(activation['name'])
            activation['start'] = timestamp(activation['start'])
            activation['finish'] = timestamp(activation['finish'])
            if not activation['caller_id']:
                activation['caller_id'] = 'nil'
            result.append(
                'activation('
                    '{trial_id}, {id}, {name!r}, {start:-f}, {finish:-f}, '
                    '{caller_id}).'
                ''.format(**activation))

    def export_trial_file_accesses(self, result, with_doc=True):
        if with_doc:
            result.append(textwrap.dedent("""
                %
                % FACT: access(trial_id, id, name, mode, content_hash_before, content_hash_after, timestamp, activation_id).
                %
                """))
        result.append(":- dynamic(access/8).")
        for access in self.trial.file_accesses():
            access = dict(access)
            access['trial_id'] = self.trial.id
            access['name'] = str(access['name'])
            access['mode'] = str(access['mode'])
            access['buffering'] = str(access['buffering'])
            access['content_hash_before'] = str(access['content_hash_before'])
            access['content_hash_after'] = str(access['content_hash_after'])
            access['timestamp'] = timestamp(access['timestamp'])
            result.append(
                'access('
                    '{trial_id}, {id}, {name!r}, {mode!r}, '
                    '{content_hash_before!r}, {content_hash_after!r}, '
                    '{timestamp:-f}, {function_activation_id}).'
                ''.format(**access))

    def export_trial_slicing_variables(self, result, with_doc=True):
        if with_doc:
            result.append(textwrap.dedent("""
                %
                % FACT: variable(trial_id, vid, name, line, value, timestamp).
                %
                """))
        result.append(":- dynamic(variable/6).")
        for var in self.trial.slicing_variables():
            var = dict(var)
            var['vid'] = str(var['vid'])
            var['name'] = str(var['name'])
            var['line'] = str(var['line'])
            var['value'] = str(var['value'])
            var['time'] = timestamp(var['time'])
            result.append(
                'variable('
                    '{trial_id}, {vid}, {name!r}, {line}, {value!r}, '
                    '{time:-f}).'
                ''.format(**var))

    def export_trial_slicing_usages(self, result, with_doc=True):
        if with_doc:
            result.append(textwrap.dedent("""
                %
                % FACT: usage(trial_id, id, vid, name, line).
                %
                """))
        result.append(":- dynamic(usage/5).")
        for usage in self.trial.slicing_usages():
            usage = dict(usage)
            usage['id'] = str(usage['id'])
            usage['vid'] = str(usage['vid'])
            usage['name'] = str(usage['name'])
            usage['line'] = str(usage['line'])
            result.append(
                'usage('
                    '{trial_id}, {id}, {vid}, {name!r}, {line}).'
                ''.format(**usage))

    def export_trial_slicing_dependencies(self, result, with_doc=True):
        if with_doc:
            result.append(textwrap.dedent("""
                %
                % FACT: dependency(trial_id, id, dependent, supplier).
                %
                """))
        result.append(":- dynamic(dependency/4).")
        for dep in self.trial.slicing_dependencies():
            dep = dict(dep)
            dep['id'] = str(dep['id'])
            dep['dependent'] = str(dep['dependent'])
            dep['supplier'] = str(dep['supplier'])
            result.append(
                'dependency('
                    '{trial_id}, {id}, {dependent}, {supplier}).'
                ''.format(**dep))

    def export_facts(self, with_doc=True):
        # TODO: export remaining data
        # (now focusing only on activation, file access and slices)
        result = []
        self.export_trial_activations(result, with_doc)
        self.export_trial_file_accesses(result, with_doc)
        self.export_trial_slicing_variables(result, with_doc)
        self.export_trial_slicing_usages(result, with_doc)
        self.export_trial_slicing_dependencies(result, with_doc)
        return result

    def export_text_facts(self):
        return u'\n'.join(self.export_facts())

    def export_rules(self):
        return resource(RULES, 'UTF-8')

    def load_cli_facts(self):
        self.init_cli()
        load_trial = 'load_trial({})'.format(self.id)
        if not list(self.prolog_cli.query(load_trial)):
            for fact in self.export_facts(with_doc=False):
                self.prolog_cli.assertz(fact[:-1])
            self.prolog_cli.assertz(load_trial)
        load_rules = 'load_rules(1)'
        if not list(self.prolog_cli.query(load_rules)):
            for rule in self.export_rules().split('\n'):
                rule = rule.strip()
                if not rule or rule[0] == '%':
                    continue
                self.prolog_cli.assertz(rule[:-1])
            self.prolog_cli.assertz(load_rules)

    def query(self, query):
        self.load_cli_facts()
        return self.prolog_query(query)

    @classmethod
    def init_cli(cls):
        if not cls.prolog_cli:
            from pyswip import Prolog
            cls.prolog_cli = Prolog()
            cls.prolog_cli.assertz('load_trial(0)')
            cls.prolog_cli.assertz('load_rules(0)')

    @classmethod
    def prolog_query(cls, query):
        cls.init_cli()
        return cls.prolog_cli.query(query)
