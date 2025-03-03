import frappe

def update_returned_items(doc, method):
    """
    Updates 'custom_is_returned' in both the returned invoice and the original sales invoice.
    """
    if doc.is_return and doc.return_against:
        frappe.logger().info(f"Processing return invoice: {doc.name}, Return Against: {doc.return_against}")

        # Fetch original items from the parent invoice using SQL
        original_items = frappe.db.sql("""
            SELECT name, item_code FROM `tabSales Invoice Item`
            WHERE parent=%s
        """, (doc.return_against,), as_dict=True)

        original_items_dict = {item["item_code"]: item["name"] for item in original_items}
        frappe.logger().info(f"Original items from invoice {doc.return_against}: {original_items_dict}")

        for item in doc.items:
            if item.item_code in original_items_dict and item.qty < 0:
                item.custom_is_returned = 1  # Mark as returned in the return invoice
                frappe.logger().info(f"Item {item.item_code} marked as returned in return invoice.")

                # Also update the original invoice's item
                frappe.db.set_value("Sales Invoice Item", original_items_dict[item.item_code], "custom_is_returned", 1)
                frappe.logger().info(f"Item {item.item_code} marked as returned in original invoice.")

            else:
                item.custom_is_returned = 0  # Not returned in return invoice

        # Commit changes to ensure the database updates
        frappe.db.commit()
