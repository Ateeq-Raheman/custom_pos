import frappe
from frappe import _

def search_invoices_for_return(doctype, txt, searchfield, start, page_len, filters):
    """
    This function overrides POS Awesome's default behavior by:
    - Removing already returned items from invoices instead of hiding the whole invoice.
    - Hiding invoices where all items have been returned.
    """
    
    # Fetch all Sales Invoices that are eligible for return (not return invoices)
    invoices = frappe.db.get_list(
        "Sales Invoice",
        fields=["name", "customer", "posting_date", "total", "items"],
        filters={"docstatus": 1, "is_return": 0},
        order_by="modified desc"
    )

    # Fetch all return invoices and their returned items
    returned_invoices = frappe.db.get_list(
        "Sales Invoice",
        fields=["return_against", "items"],
        filters={"is_return": 1}
    )

    # Create a dictionary mapping original invoices to their returned items
    returned_items_mapping = {}

    for inv in returned_invoices:
        if inv.return_against:
            returned_items_mapping.setdefault(inv.return_against, []).extend(
                [item["item_code"] for item in frappe.parse_json(inv.items)]
            )

    # Filter invoices: Remove already returned items, hide invoices if all items are returned
    filtered_invoices = []
    for invoice in invoices:
        original_items = frappe.parse_json(invoice["items"])  # Convert item data
        if invoice["name"] in returned_items_mapping:
            invoice["items"] = [
                item for item in original_items
                if item["item_code"] not in returned_items_mapping[invoice["name"]]
            ]
        
        # Only add the invoice if there are remaining items to return
        if invoice["items"]:
            filtered_invoices.append(invoice)

    return filtered_invoices
