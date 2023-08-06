# coding: utf-8

"""
Graphical statistics about emails traffic using RRDtool

This module provides support to retrieve statistics from postfix log :
sent, received, bounced, rejected

"""
from django.utils.translation import ugettext_lazy

from modoboa.core.extensions import ModoExtension, exts_pool
from modoboa.lib import events, parameters


class Stats(ModoExtension):
    name = "modoboa_stats"
    label = "Statistics"
    version = "1.0.0"
    description = ugettext_lazy(
        "Graphical statistics about emails traffic using RRDtool"
    )
    needs_media = True
    url = "stats"

    def load(self):
        from .app_settings import ParametersForm

        events.declare(["GetGraphSets"])
        parameters.register(
            ParametersForm, ugettext_lazy("Graphical statistics")
        )
        from . import general_callbacks

exts_pool.register_extension(Stats)
