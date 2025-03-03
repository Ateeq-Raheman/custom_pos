import frappe

@frappe.whitelist()
def get_sales_invoice_child_table(invoice_no=None):
    """
    Custom override function to fetch sales invoice child table
    without showing any message.
    """
    if not invoice_no:
        return {"error": "Missing invoice_no"}

    return frappe.get_all("Sales Invoice Item",
        filters={"parent": invoice_no},
        fields=["item_code", "qty", "rate", "amount"])
