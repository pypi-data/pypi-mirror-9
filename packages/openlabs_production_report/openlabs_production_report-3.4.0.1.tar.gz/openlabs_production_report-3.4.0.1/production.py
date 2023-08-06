# -*- coding: utf-8 -*-
"""
    production.py

    :copyright: (c) 2014-2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from dateutil.relativedelta import relativedelta
from datetime import date
from operator import attrgetter
from itertools import groupby, izip_longest
from openlabs_report_webkit import ReportWebkit
from sql.conditionals import Coalesce

from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta
from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateAction, StateView, Button
from trytond.report import Report
from trytond.exceptions import UserError


__metaclass__ = PoolMeta
__all__ = [
    'ProductionReport', 'ProductionScheduleReport',
    'ProductionScheduleReportWizardStart', 'ProductionScheduleReportWizard',
    'Production'
]


class ReportMixin(ReportWebkit):
    """
    Mixin Class to inherit from, for all HTML reports.
    """

    @classmethod
    def wkhtml_to_pdf(cls, data, options=None):
        """
        Call wkhtmltopdf to convert the html to pdf
        """
        Company = Pool().get('company.company')

        company = ''
        if Transaction().context.get('company'):
            company = Company(Transaction().context.get('company')).party.name
        options = {
            'margin-bottom': '0.50in',
            'margin-left': '0.50in',
            'margin-right': '0.50in',
            'margin-top': '0.50in',
            'footer-font-size': '8',
            'footer-left': company,
            'footer-line': '',
            'footer-right': '[page]/[toPage]',
            'footer-spacing': '5',
        }
        return super(ReportMixin, cls).wkhtml_to_pdf(
            data, options=options
        )


class ProductionReport(ReportMixin):
    """
    Production Report
    """
    __name__ = 'production.report'


class ProductionScheduleReport(Report):
    """
    Production Schedule Report
    """
    __name__ = 'report.production.schedule'

    @classmethod
    def parse(cls, report, records, data, localcontext):
        """
        Data must always contain a key 'productions' if records is None
        """
        Production = Pool().get('production')

        key = attrgetter('reporting_date')

        if not records:
            records = Production.browse(data['productions'])

        productions = Production.search([
            ('id', 'in', map(int, records)),
            ('reporting_date', '!=', None)
        ], order=[('reporting_date', 'ASC')])

        # Raise UserError if no productions were found
        if not productions:  # pragma: no cover
            raise UserError(
                "No Productions found for the given date range"
            )

        matrix = []
        for reporting_date, prod_on_date in groupby(productions, key=key):
            matrix.append([reporting_date] + list(prod_on_date))

        # Transpose the array
        productions_by_date = list(izip_longest(*matrix))

        localcontext.update({
            'productions_by_date': productions_by_date[1:],
            'dates': productions_by_date[0]
        })
        return super(ProductionScheduleReport, cls).parse(
            report, records, data, localcontext
        )


class ProductionScheduleReportWizardStart(ModelView):
    'Generate Production Schedule Report'
    __name__ = 'report.production.schedule.wizard.start'

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)

    @staticmethod
    def default_start_date():  # pragma: no cover
        """
        Set default start date to the Monday of current week
        """
        today = date.today()

        if today.weekday() == 6:
            # This is to make sure we get monday of current week in case
            # today is Sunday
            return today + relativedelta(days=1)
        return today - relativedelta(days=today.weekday())

    @staticmethod
    def default_end_date():  # pragma: no cover
        """
        Set default end date to the Saturday of current week
        """
        today = date.today()

        if today.weekday() == 6:
            # This is to make sure we get Saturday of current week in case
            # today is Sunday
            return today + relativedelta(days=6)
        return (
            today - relativedelta(days=today.weekday()) + relativedelta(days=5)
        )


class ProductionScheduleReportWizard(Wizard):
    'Generate Production Schedule Report Wizard'
    __name__ = 'report.production.schedule.wizard'

    start = StateView(
        'report.production.schedule.wizard.start',
        'production_report.report_production_schedule_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Generate', 'generate', 'tryton-ok', default=True),
        ]
    )
    generate = StateAction(
        'production_report.report_production_schedule'
    )

    def do_generate(self, action):
        """
        Return report action and the data to pass to it
        """
        Production = Pool().get('production')

        domain = [
            ('state', 'not in', ['request', 'cancel']),
            [
                'OR',
                ('effective_date', '>=', self.start.start_date),
                ('planned_date', '>=', self.start.start_date)
            ],
            [
                'OR',
                ('effective_date', '<=', self.start.end_date),
                ('planned_date', '<=', self.start.end_date)
            ],
        ]

        productions = Production.search(domain)

        data = {
            'productions': map(int, productions),
            'start_date': self.start.start_date,
            'end_date': self.start.end_date
        }
        return action, data

    def transition_generate(self):
        return 'end'


class Production:
    __name__ = 'production'

    reporting_date = fields.Function(
        fields.Date('Reporting Date'), 'get_reporting_date',
        searcher='search_reporting_date'
    )

    def get_reporting_date(self, name):
        return self.effective_date if self.effective_date else self.planned_date

    @staticmethod
    def order_reporting_date(tables):
        table, _ = tables[None]
        return [Coalesce(table.effective_date, table.planned_date)]

    @classmethod
    def search_reporting_date(cls, name, clause):
        return [
            'OR',
            ('effective_date',) + tuple(clause[1:]),
            ('planned_date',) + tuple(clause[1:])
        ]
