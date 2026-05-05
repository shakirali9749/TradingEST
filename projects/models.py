from decimal import Decimal

from django.db import models


class Project(models.Model):
    """Master project / job — links to transactions by FK."""

    name = models.CharField(max_length=255, unique=True)
    client_name = models.CharField(max_length=255, blank=True)
    contract_value_excl_vat = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def vat_15(self):
        """ROUND(contract × 0.15, 2) — Business-Logic §5 rule 2."""
        if self.contract_value_excl_vat is None:
            return None
        return (self.contract_value_excl_vat * Decimal("0.15")).quantize(Decimal("0.01"))

    @property
    def contract_incl_vat(self):
        if self.contract_value_excl_vat is None or self.vat_15 is None:
            return None
        return self.contract_value_excl_vat + self.vat_15

    @property
    def required_advance_50_incl_vat(self):
        """50% × Contract Incl. VAT — Business-Logic §5 rule 3."""
        ci = self.contract_incl_vat
        if ci is None:
            return None
        return (ci * Decimal("0.5")).quantize(Decimal("0.01"))
