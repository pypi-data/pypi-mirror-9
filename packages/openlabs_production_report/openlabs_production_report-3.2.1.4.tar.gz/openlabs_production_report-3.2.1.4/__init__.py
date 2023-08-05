# -*- coding: utf-8 -*-
"""
    __init__.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool
from production import ProductionReport, ProductionScheduleReport, \
    ProductionScheduleReportWizardStart, ProductionScheduleReportWizard, \
    Production


def register():
    Pool.register(
        ProductionReport,
        ProductionScheduleReport,
        module='production_report', type_='report'
    )
    Pool.register(
        ProductionScheduleReportWizardStart,
        Production,
        module='production_report', type_='model'
    )
    Pool.register(
        ProductionScheduleReportWizard,
        module='production_report', type_='wizard'
    )
