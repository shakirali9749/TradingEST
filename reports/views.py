import calendar
from datetime import date

from django.views.generic import TemplateView

from accounts.mixins import AccountantOrAdminRequiredMixin, SessionAuthenticatedMixin
from accounts.models import Role

from .services import (
    accounts_summary_rows,
    dashboard_metrics,
    latest_transaction_month,
    monthly_report_for_month,
    tax_report_for_period,
)


class DashboardView(SessionAuthenticatedMixin, TemplateView):
    template_name = "reports/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        role = getattr(user, "role", None)
        ctx["show_full_financial_dashboard"] = role in (
            Role.ACCOUNTANT,
            Role.ADMIN,
        )
        ctx["show_admin_shortcuts"] = role == Role.ADMIN

        y_raw = self.request.GET.get("year")
        m_raw = self.request.GET.get("month")
        try:
            y = int(y_raw) if y_raw else None
            m = int(m_raw) if m_raw else None
        except ValueError:
            y, m = None, None

        # Default VAT period: latest month that has transactions (explicit workbook tie-in)
        if not y or not m or not (1 <= m <= 12):
            lm = latest_transaction_month()
            if lm:
                y, m = lm
            else:
                t = date.today()
                y, m = t.year, t.month

        ctx["calendar_months"] = [(i, calendar.month_name[i]) for i in range(1, 13)]
        ctx["metrics"] = dashboard_metrics(y, m)
        ctx["year"] = y
        ctx["month"] = m
        ctx["month_name"] = calendar.month_name[m]
        return ctx


class AccountsSummaryView(AccountantOrAdminRequiredMixin, TemplateView):
    template_name = "reports/accounts_summary.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["rows"] = accounts_summary_rows()
        return ctx


class TaxReportView(AccountantOrAdminRequiredMixin, TemplateView):
    template_name = "reports/tax_report.html"

    PERIOD_OPTIONS = (
        (1, "1 month", "Single month only"),
        (3, "3 months", "Last 3 calendar months"),
        (6, "6 months", "Half-year view"),
        (9, "9 months", "Nine-month view"),
        (12, "12 months", "Full year (12 months)"),
    )

    def _year_choices(self) -> list[int]:
        today = date.today()
        start = today.year - 5
        lm = latest_transaction_month()
        if lm:
            start = min(start, lm[0])
        return list(range(today.year + 1, start - 1, -1))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["calendar_months"] = [(i, calendar.month_name[i]) for i in range(1, 13)]
        ctx["period_options"] = self.PERIOD_OPTIONS
        ctx["year_choices"] = self._year_choices()
        allowed_periods = {n for n, _, _ in self.PERIOD_OPTIONS}

        today = date.today()
        y, m = today.year, today.month
        lm = latest_transaction_month()
        if lm:
            y, m = lm
        months = 1

        if "year" in self.request.GET and "month" in self.request.GET:
            try:
                y = int(self.request.GET.get("year"))
                m = int(self.request.GET.get("month"))
                months = int(self.request.GET.get("months", "1"))
            except (TypeError, ValueError):
                pass

        if not (1 <= m <= 12):
            m = today.month
        if months not in allowed_periods:
            months = 1

        ctx["report"] = tax_report_for_period(y, m, months)
        ctx["year"] = y
        ctx["month"] = m
        ctx["months"] = months
        ctx["end_month_name"] = calendar.month_name[m]
        return ctx


class MonthlyReportView(AccountantOrAdminRequiredMixin, TemplateView):
    template_name = "reports/monthly_report.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["calendar_months"] = [(i, calendar.month_name[i]) for i in range(1, 13)]

        today = date.today()
        y, m = today.year, today.month
        lm = latest_transaction_month()
        if lm:
            y, m = lm

        if "year" in self.request.GET and self.request.GET.get("year", "").strip():
            try:
                y = int(self.request.GET.get("year"))
            except (TypeError, ValueError):
                y = today.year
        if "month" in self.request.GET:
            try:
                m = int(self.request.GET.get("month"))
            except (TypeError, ValueError):
                m = today.month

        if not (2000 <= y <= 2100):
            y = today.year
        if not (1 <= m <= 12):
            m = today.month

        ctx["report"] = monthly_report_for_month(y, m)
        ctx["year"] = y
        ctx["month"] = m
        ctx["month_name"] = calendar.month_name[m]
        return ctx
