from datetime import date

from django.views.generic import TemplateView

from accounts.mixins import AccountantOrAdminRequiredMixin, SessionAuthenticatedMixin
from accounts.models import Role

from .services import (
    accounts_summary_rows,
    dashboard_metrics,
    latest_transaction_month,
    monthly_report_for_month,
    tax_report_for_month,
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

        ctx["metrics"] = dashboard_metrics(y, m)
        ctx["year"] = y
        ctx["month"] = m
        return ctx


class AccountsSummaryView(AccountantOrAdminRequiredMixin, TemplateView):
    template_name = "reports/accounts_summary.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["rows"] = accounts_summary_rows()
        return ctx


class TaxReportView(AccountantOrAdminRequiredMixin, TemplateView):
    template_name = "reports/tax_report.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        msg = "Please select a month and year to generate the report."

        if "year" not in self.request.GET or "month" not in self.request.GET:
            ctx["report_ready"] = False
            ctx["report"] = None
            ctx["year"] = ""
            ctx["month"] = ""
            ctx["report_message"] = msg
            return ctx

        try:
            y = int(self.request.GET.get("year"))
            m = int(self.request.GET.get("month"))
        except (TypeError, ValueError):
            ctx["report_ready"] = False
            ctx["report"] = None
            ctx["year"] = self.request.GET.get("year", "")
            ctx["month"] = self.request.GET.get("month", "")
            ctx["report_message"] = msg
            return ctx

        if not (1 <= m <= 12):
            ctx["report_ready"] = False
            ctx["report"] = None
            ctx["year"] = y
            ctx["month"] = m
            ctx["report_message"] = msg
            return ctx

        ctx["report_ready"] = True
        ctx["report"] = tax_report_for_month(y, m)
        ctx["year"] = y
        ctx["month"] = m
        ctx["report_message"] = ""
        return ctx


class MonthlyReportView(AccountantOrAdminRequiredMixin, TemplateView):
    template_name = "reports/monthly_report.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        msg = "Please select a month and year to generate the report."

        if "year" not in self.request.GET or "month" not in self.request.GET:
            ctx["report_ready"] = False
            ctx["report"] = None
            ctx["year"] = ""
            ctx["month"] = ""
            ctx["report_message"] = msg
            return ctx

        try:
            y = int(self.request.GET.get("year"))
            m = int(self.request.GET.get("month"))
        except (TypeError, ValueError):
            ctx["report_ready"] = False
            ctx["report"] = None
            ctx["year"] = self.request.GET.get("year", "")
            ctx["month"] = self.request.GET.get("month", "")
            ctx["report_message"] = msg
            return ctx

        if not (1 <= m <= 12):
            ctx["report_ready"] = False
            ctx["report"] = None
            ctx["year"] = y
            ctx["month"] = m
            ctx["report_message"] = msg
            return ctx

        ctx["report_ready"] = True
        ctx["report"] = monthly_report_for_month(y, m)
        ctx["year"] = y
        ctx["month"] = m
        ctx["report_message"] = ""
        return ctx
