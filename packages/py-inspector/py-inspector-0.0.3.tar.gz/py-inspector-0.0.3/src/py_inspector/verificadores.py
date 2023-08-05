# -*- coding: utf-8 -*-
import unittest
import pep8
from nose.tools import assert_true
from pylint import lint
from pylint.reporters.text import TextReporter


class CustomReport(pep8.StandardReport):
    results = []

    def __init__(self, options):
        super(CustomReport, self).__init__(options)
        self.results = []

    def get_file_results(self):
        if self._deferred_print:
            self._deferred_print.sort()
            for line_number, offset, code, text, _ in self._deferred_print:
                self.results.append({
                    'path': self.filename,
                    'row': self.line_offset + line_number,
                    'col': offset + 1,
                    'code': code,
                    'text': text,
                })
        return self.file_errors


class WritableObject(object):
    def __init__(self):
        self.content = []

    def write(self, st):
        if st == '\n':
            return
        if '*****' in st:
            return
        self.content.append(st)

    def read(self):
        return self.content


class TestValidacaoPython(object):
    def validacao_pep8(self, arquivos):
        pep8style = pep8.StyleGuide(reporter=CustomReport)
        report = pep8style.init_report()
        pep8style.check_files(arquivos)
        for error in report.results:
            if error['code'] == 'E501':
                continue
            msg = "PEP8 em {path}:{row}:{col} - {code}: {text}"
            assert_true(False, msg.format(
                path=error['path'],
                code=error['code'],
                row=error['row'],
                col=error['col'],
                text=error['text']
            ))

    def validacao_pylint(self, arquivos):
        args = [
            "-r",
            "n",
            "--msg-template='Pylint em {path}:{line}:{column} [{msg_id}: {msg} em {obj}]'",
            '--disable=C0301,R0201,R0903',
            '--class-attribute-rgx=([A-Za-z_][A-Za-z0-9_]{2,60}|(__.*__))$',
            '--max-args=8'
        ]
        pylint_output = WritableObject()
        lint.Run(arquivos + args, reporter=TextReporter(pylint_output), exit=False)
        for line in pylint_output.read():
            assert_true(False, line)
