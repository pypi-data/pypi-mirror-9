# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..utils.text import mark_for_translation as _

ZEN = _("""
      ,
     @@
   @@@@
  @@@@@
  @@@@@
  @@@@@
  @@@@@
  @@@@@
  @@@@@                       '@@@@@@,          .@@@@@@+           +@@@@@@.
  @@@@@@,                  `@@@@@@@           +@@@@@@,          `@@@@@@#
  @@@@@@@@+              :@@@@@@'          `@@@@@@@           ;@@@@@@:
  @@@@@@@@@@@`         #@@@@@@.          :@@@@@@'           @@@@@@@`
  @@@@@ ;@@@@@@;    .@@@@@@#           #@@@@@@`          ,@@@@@@+
  @@@@@   `@@@@@@#'@@@@@@:          .@@@@@@+           +@@@@@@.
  @@@@@      +@@@@@@@@@           +@@@@@@,          `@@@@@@#
  @@@@@        ,@@@@@@+        `@@@@@@@@@`        ;@@@@@@:
  @@@@@           @@@@@@@`   :@@@@@@'@@@@@@'    @@@@@@@`
  @@@@@             ;@@@@@@#@@@@@@`   `@@@@@@@@@@@@@+
  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@#         +@@@@@@@@.
  @@@@@@@@@@@@@@@@@@@@@@@@@@@,             .@@@#


  The Zen of BundleWrap
  ─────────────────────

  BundleWrap is a tool, not a solution.
  BundleWrap will not write your configuration for you.
  BundleWrap is Python all the way down.
  BundleWrap will adapt rather than grow.
  BundleWrap is the single point of truth.
""")

def bw_zen(repo, args):
    for line in ZEN.split("\n"):
        yield line
