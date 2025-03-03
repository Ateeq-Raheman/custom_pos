import frappe

def update_returned_items(doc, method):
    """
    Updates the 'custom_is_returned' field in the child table of Sales Invoice
    when an item is returned.
    """
    if doc.is_return and doc.return_against:
        # Get the original invoice items
        original_items = frappe.get_all("Sales Invoice Item",
            filters={"parent": doc.return_against},
            fields=["item_code", "qty"])

        # Convert list to dictionary for easy lookup
        original_items_dict = {item["item_code"]: item["qty"] for item in original_items}

        for item in doc.items:
            # If the item exists in the original invoice and has a negative quantity (returned)
            if item.item_code in original_items_dict and item.qty < 0:
                item.custom_is_returned = 1  # Mark as returned
            else:
                item.custom_is_returned = 0  # Not returned

