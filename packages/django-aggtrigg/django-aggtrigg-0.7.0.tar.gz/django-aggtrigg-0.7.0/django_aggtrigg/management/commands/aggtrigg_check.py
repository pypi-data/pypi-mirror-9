#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Rodolphe Quiédeville <rodolphe@quiedeville.org>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of django-aggtrigg nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
import sys
from django.core.management.base import BaseCommand
from django.conf import settings
from optparse import make_option
from ... import util
from .. import djutil

STATUS = ['OK', 'KO']


class Command(BaseCommand):
    """Check database coherence with models
    """
    help = 'Import datas'
    option_list = BaseCommand.option_list + (
        make_option("-d",
                    "--database",
                    dest="database",
                    type="string",
                    help="database name",
                    default="default"),)

    def handle(self, *args, **options):
        """Handle action
        """
        trigs = djutil.get_agg_fields()
        sys.stdout.write("--found %d triggers\n" % (len(trigs)))
        for trig in trigs:
            self.check_trigger(trig, options)

    def check_trigger(self, trig, options):
        """Check database for a trigger

        trig : {'table': u'apple_apple',
        'model': <class 'foo.apple.models.Apple'>,
         'aggs': ['max'],
         'field': 'indice'}
        """
        aggs = trig['aggs']
        table = trig['table']
        model = trig["model"]
        column = model._meta.get_field(trig['field']).attname
        engine = settings.DATABASES[options['database']]['ENGINE']

        agg = util.AggTrigger(engine, table, column,
                              aggs, model=model)

        agg.verbose = int(options['verbosity'])

        comment = "\n".join(["--",
                             "-- model: %s",
                             "-- source: %s, column: %s, aggregats: %s"])

        if table and trig['field'] and len(aggs) > 0:
            sys.stdout.write(comment % (trig['model'], table,
                                        trig['field'], aggs))
            if agg.agg_table_ispresent():
                msg = "OK table: %s is present\n" % (agg.table_name)
            else:
                msg = "KO table: %s is absent\n" % (agg.table_name)

            sys.stdout.write(msg)

            for trig in agg.triggers_on_table_are_present():
                if trig[1]:
                    msg = "OK trigger: %s is present\n" % (trig[0])
                else:
                    msg = "KO trigger: %s is absent\n" % (trig[0])
                sys.stdout.write(msg)

            for func in agg.functions_are_present():
                if func[1]:
                    msg = "OK function: %s is present\n" % (func[0])
                else:
                    msg = "KO function: %s is absent\n" % (func[0])
                sys.stdout.write(msg)
