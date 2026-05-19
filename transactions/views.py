from django.db.models import Count, F, Q, Sum
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from accounts.mixins import (
    AccountantOrAdminRequiredMixin,
    AdminOrAccountantMixin,
    SessionAuthenticatedMixin,
    ViewerReadOnlyMixin,
)

from .forms import LegacyPayableForm, TransactionForm
from .models import LegacyPayable, Transaction


class TransactionListView(ViewerReadOnlyMixin, ListView):
    model = Transaction
    template_name = "transactions/transaction_list.html"
    context_object_name = "transactions"
    paginate_by = 50

    def get_queryset(self):
        qs = (
            Transaction.objects.select_related("project")
            .annotate(
                project_name=F("project__name"),
            )
            .order_by("-date", "-pk")
        )
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(reference_number__icontains=q)
                | Q(description__icontains=q)
                | Q(party_name__icontains=q)
                | Q(notes__icontains=q)
                | Q(invoice_number__icontains=q)
            )
        acc = self.request.GET.get("account", "").strip()
        if acc:
            qs = qs.filter(account__iexact=acc)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        filtered_qs = self.get_queryset()
        agg = filtered_qs.aggregate(
            total_lines=Count("id"),
            sum_excl=Sum("amount_excl_vat"),
            sum_total=Sum("total_amount"),
        )
        ctx["filters"] = {"q": self.request.GET.get("q", ""), "account": self.request.GET.get("account", "")}
        ctx["ledger_totals"] = agg
        ctx["filters_active"] = bool(
            self.request.GET.get("q", "").strip() or self.request.GET.get("account", "").strip()
        )
        ctx["account_breakdown"] = (
            filtered_qs.values("account")
            .annotate(lines=Count("id"), sum_excl=Sum("amount_excl_vat"))
            .order_by("account")
        )
        return ctx


class TransactionDetailView(SessionAuthenticatedMixin, DetailView):
    model = Transaction
    template_name = "transactions/transaction_detail.html"
    context_object_name = "transaction"

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        ref = self.kwargs.get("reference_number")
        if ref:
            return get_object_or_404(queryset, reference_number__iexact=ref.strip())
        return super().get_object(queryset)

    def get_queryset(self):
        return Transaction.objects.select_related("project").annotate(
            project_name=F("project__name"),
        )


class TransactionCreateView(AdminOrAccountantMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "transactions/transaction_form.html"

    def get_success_url(self):
        return reverse_lazy(
            "transactions:detail_by_ref",
            kwargs={"reference_number": self.object.reference_number},
        )


class TransactionUpdateView(AdminOrAccountantMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "transactions/transaction_form.html"

    def get_queryset(self):
        return Transaction.objects.select_related("project")

    def get_success_url(self):
        return reverse_lazy(
            "transactions:detail_by_ref",
            kwargs={"reference_number": self.object.reference_number},
        )


class TransactionDeleteView(AdminOrAccountantMixin, DeleteView):
    model = Transaction
    template_name = "transactions/transaction_confirm_delete.html"
    success_url = reverse_lazy("transactions:list")


class LegacyPayableListView(AccountantOrAdminRequiredMixin, ListView):
    model = LegacyPayable
    template_name = "transactions/legacy_list.html"
    context_object_name = "legacy_rows"

    def get_queryset(self):
        return LegacyPayable.objects.annotate(
            remaining_calc=F("total_payable") - F("total_paid"),
        ).order_by("supplier_name", "pk")


class LegacyPayableCreateView(AdminOrAccountantMixin, CreateView):
    model = LegacyPayable
    form_class = LegacyPayableForm
    template_name = "transactions/legacy_form.html"
    success_url = reverse_lazy("transactions:legacy_list")


class LegacyPayableUpdateView(AdminOrAccountantMixin, UpdateView):
    model = LegacyPayable
    form_class = LegacyPayableForm
    template_name = "transactions/legacy_form.html"
    success_url = reverse_lazy("transactions:legacy_list")


class LegacyPayableDeleteView(AdminOrAccountantMixin, DeleteView):
    model = LegacyPayable
    template_name = "transactions/legacy_confirm_delete.html"
    success_url = reverse_lazy("transactions:legacy_list")
