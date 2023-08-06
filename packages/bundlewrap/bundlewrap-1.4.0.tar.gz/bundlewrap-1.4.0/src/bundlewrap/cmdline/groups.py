# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..utils import names


def bw_groups(repo, args):
    for group in repo.groups:
        line = group.name
        if args['show_nodes']:
            line += ": " + ", ".join(names(group.nodes))
        yield line
