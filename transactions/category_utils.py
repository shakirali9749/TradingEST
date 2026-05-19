"""Category choices for transactions — defaults plus any used in the ledger."""

from .models import LedgerCategory, Transaction

ADD_CATEGORY_VALUE = "__add_category__"
ADD_CATEGORY_LABEL = "+ Add category"


def normalize_category_name(raw: str | None) -> str:
    return " ".join(str(raw or "").strip().split())


def all_category_names() -> list[str]:
    defaults = [choice.value for choice in LedgerCategory]
    custom = (
        Transaction.objects.exclude(category="")
        .values_list("category", flat=True)
        .distinct()
    )
    return sorted(set(defaults) | set(custom), key=str.casefold)


def category_field_choices(include_blank: bool = True) -> list[tuple[str, str]]:
    choices = [(name, name) for name in all_category_names()]
    if include_blank:
        return [("", "---------")] + choices
    return choices
