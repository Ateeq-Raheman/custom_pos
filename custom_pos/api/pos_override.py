import frappe

@frappe.whitelist()
def search_invoices_for_return():
    invoices = frappe.get_all(
        "Sales Invoice",
        filters={"is_return": 0},
        fields=["name", "customer", "total", "status"]
    )

    filtered_invoices = []
    for invoice in invoices:
        items = frappe.get_all(
            "Sales Invoice Item",
            filters={"parent": invoice["name"]},
            fields=["item_code", "qty"]
        )

        returned_items = frappe.get_all(
            "Sales Invoice Item",
            filters={"return_against": invoice["name"]},
            fields=["item_code", "qty"]
        )

        remaining_items = []
        for item in items:
            returned_qty = sum(
                ret["qty"] for ret in returned_items if ret["item_code"] == item["item_code"]
            )
            if item["qty"] > returned_qty:
                remaining_items.append(item)

        if remaining_items:
            invoice["items"] = remaining_items
            filtered_invoices.append(invoice)

    return filtered_invoices
