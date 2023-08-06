#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import errno
import os

from sphinx.application import Sphinx
from sphinx.ext.doctest import DocTestBuilder


class SphinxDocTestCollectorBuilder(DocTestBuilder):
    """A fake Sphinx builder that collects tests from docs.
    """
    def __init__(self, app, into, excludes):
        super(SphinxDocTestCollectorBuilder, self).__init__(app)
        self.into = into
        self.excludes = excludes

    def test_group(self, group, filename):
        if filename not in self.excludes:
            self.into.append((filename, group,))


class DocTestCollector(Sphinx):

    def __init__(self, groups, excludes, **options):
        options.update({
            'buildername': 'doctest',   # Pretend that we're running doctests.
            'status': None,             # Silence Sphinx output.
            'warning': None,
        })
        super(DocTestCollector, self).__init__(**options)

        # Swap-out Sphinx's doctest builder with our own.
        self.builder = SphinxDocTestCollectorBuilder(
            app=self, into=groups, excludes=excludes,
        )


def make_build_dirs(builddir):
    outdir = os.path.join(builddir, 'doctest')
    doctreedir = os.path.join(builddir, 'doctrees')

    build_dirs = (outdir, doctreedir,)
    for build_dir in build_dirs:
        try:
            os.mkdir(build_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    return build_dirs


def collect_sphinx_doctests(srcdir, confdir, builddir, excludes):
    """Collect doctests from a Sphinx documentation setup.
    """
    outdir, doctreedir = make_build_dirs(builddir)

    groups = []

    # Run Sphinx to collect doctest groups.
    sphinx = DocTestCollector(
        groups=groups, srcdir=srcdir, confdir=confdir, outdir=outdir,
        doctreedir=doctreedir, excludes=excludes,
    )
    sphinx.builder.build_update()
    sphinx.builder.cleanup()

    return groups
