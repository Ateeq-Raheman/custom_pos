import frappe
from frappe import _

@frappe.whitelist()
def search_invoices_for_return(txt="", start=0, page_len=20, filters=None):
    """
    Custom function to filter invoices for return in POS Awesome.
    - Excludes fully returned invoices.
    - Shows invoices with unreturned items.
    """

    filters = filters or {}

    try:
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
                except Exception as e:
                    frappe.logger().error(f"Error parsing returned invoice items: {str(e)}")
                    continue  # Skip if JSON parsing fails

        # Filter invoices based on returned items
        filtered_invoices = []
        for invoice in invoices:
            try:
                original_items = frappe.parse_json(invoice["items"])  # Convert item data
            except Exception as e:
                frappe.logger().error(f"Error parsing invoice items: {str(e)}")
                continue  # Skip if item data is corrupted

            # Identify non-returned items
            remaining_items = [
                item for item in original_items
                if invoice["name"] not in returned_items_mapping or item.get("item_code") not in returned_items_mapping[invoice["name"]]
            ]
            
            # Only add invoices that still have unreturned items
            if remaining_items:
                invoice["items"] = remaining_items
                filtered_invoices.append(invoice)

        # Format results for POS Awesome's expected search format
        results = [
            [inv["name"], f"{inv['name']} - {inv['customer']} - {inv['posting_date']}"]
            for inv in filtered_invoices
        ]

        return results

    except Exception as e:
        frappe.logger().error(f"Error in search_invoices_for_return: {str(e)}")
        return []