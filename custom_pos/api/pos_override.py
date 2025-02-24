import frappe
from frappe import _

@frappe.whitelist()
def search_invoices_for_return(doctype, txt, searchfield, start, page_len, filters):
    """
    Custom function to filter invoices for returns in POS Awesome.
    
    - Shows only invoices where at least one item has been returned.
    - Hides invoices where all items have been returned.
    - Shows only the remaining non-returned items in partially returned invoices.
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
        remaining_items = [
            item for item in original_items
            if invoice["name"] not in returned_items_mapping or item["item_code"] not in returned_items_mapping[invoice["name"]]
        ]
        
        # Only add the invoice if there are remaining items to return
        if remaining_items:
            invoice["items"] = remaining_items
            filtered_invoices.append(invoice)

    return filtered_invoices

