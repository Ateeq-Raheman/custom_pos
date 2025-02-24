import frappe
from frappe import _

@frappe.whitelist()
def search_invoices_for_return(doctype, txt, searchfield, start, page_len, filters):
    """
    Custom function to filter invoices for return in POS Awesome.

    - Shows only invoices where at least one item has been returned.
    - Hides invoices where all items have been returned.
    - Shows only the remaining non-returned items in partially returned invoices.
    """

    # Ensure filters exist to avoid errors
    if not filters:
        filters = {}

    # Fetch all eligible Sales Invoices (non-return invoices)
    invoices = frappe.get_all(
        "Sales Invoice",
        filters={"docstatus": 1, "is_return": 0},
        fields=["name", "customer", "posting_date", "total", "items"],
        order_by="modified desc",
        start=start,
        page_length=page_len
    )

    # Fetch all return invoices and their returned items
    returned_invoices = frappe.get_all(
        "Sales Invoice",
        filters={"is_return": 1},
        fields=["return_against", "items"]
    )

    # Create a mapping of returned items per invoice
    returned_items_mapping = {}
    for inv in returned_invoices:
        if inv.return_against:
            try:
                returned_items_mapping.setdefault(inv.return_against, []).extend(
                    [item["item_code"] for item in frappe.parse_json(inv.items) if "item_code" in item]
                )
            except Exception:
                continue  # If JSON parsing fails, ignore this entry to prevent breaking

    # Filter invoices based on returned items
    filtered_invoices = []
    for invoice in invoices:
        try:
            original_items = frappe.parse_json(invoice["items"])  # Convert item data
        except Exception:
            continue  # If item data is corrupted, ignore this invoice

        # Identify non-returned items
        remaining_items = [
            item for item in original_items
            if invoice["name"] not in returned_items_mapping or item.get("item_code") not in returned_items_mapping[invoice["name"]]
        ]
        
        # Add invoice only if it has remaining items
        if remaining_items:
            invoice["items"] = remaining_items
            filtered_invoices.append(invoice)

    # Format results for POS Awesome's expected search format
    results = [
        [inv["name"], f"{inv['name']} - {inv['customer']} - {inv['posting_date']}"]
        for inv in filtered_invoices
    ]

    return results

# Override POS Awesome method
override_whitelisted_methods = {
    "posawesome.posawesome.api.posapp.search_invoices_for_return": "custom_pos.api.pos_override.search_invoices_for_return"
}
