import frappe

def update_returned_items(doc, method):
    """
    Updates 'custom_is_returned' in Sales Invoice Item child table when an item is returned.
    """
    if doc.is_return and doc.return_against:
        frappe.logger().info(f"Processing return invoice: {doc.name}, Return Against: {doc.return_against}")

        # Fetch original items from the parent invoice using SQL (bypassing permission restrictions)
        original_items = frappe.db.sql("""
            SELECT item_code, qty FROM `tabSales Invoice Item`
            WHERE parent=%s
        """, (doc.return_against,), as_dict=True)

        original_items_dict = {item["item_code"]: item["qty"] for item in original_items}
        frappe.logger().info(f"Original items from invoice {doc.return_against}: {original_items_dict}")

        for item in doc.items:
            if item.item_code in original_items_dict and item.qty < 0:
                item.custom_is_returned = 1  # Mark as returned
                frappe.logger().info(f"Item {item.item_code} marked as returned.")
            else:
                item.custom_is_returned = 0  # Not returned
                frappe.logger().info(f"Item {item.item_code} not marked as returned.")

