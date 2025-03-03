# import frappe

# def update_returned_items(doc, method):
#     """
#     Updates 'custom_is_returned' in both the returned invoice and the original sales invoice.
#     Bypasses permission restrictions.
#     """
#     if doc.is_return and doc.return_against:
#         frappe.logger().info(f"Processing return invoice: {doc.name}, Return Against: {doc.return_against}")

#         # Fetch original items from the parent invoice using SQL (bypasses permission restrictions)
#         original_items = frappe.db.sql("""
#             SELECT name, item_code FROM `tabSales Invoice Item`
#             WHERE parent=%s
#         """, (doc.return_against,), as_dict=True)

#         original_items_dict = {item["item_code"]: item["name"] for item in original_items}
#         frappe.logger().info(f"Original items from invoice {doc.return_against}: {original_items_dict}")

#         for item in doc.items:
#             if item.item_code in original_items_dict and item.qty < 0:
#                 item.custom_is_returned = 1  # Mark as returned in the return invoice
#                 frappe.logger().info(f"Item {item.item_code} marked as returned in return invoice.")

#                 # Also update the original invoice's item (bypassing permission restrictions)
#                 frappe.db.sql("""
#                     UPDATE `tabSales Invoice Item`
#                     SET custom_is_returned = 1
#                     WHERE name = %s
#                 """, (original_items_dict[item.item_code],))

#                 frappe.logger().info(f"Item {item.item_code} marked as returned in original invoice.")

#             else:
#                 item.custom_is_returned = 0  # Not returned in return invoice

#         # Commit changes to ensure the database updates
#         frappe.db.commit()

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

import frappe

def update_returned_items(doc, method):
    """
    Updates 'custom_is_returned' in both the returned invoice and the original sales invoice.
    Bypasses permission restrictions.
    """
    if doc.is_return and doc.return_against:
        frappe.logger().info(f"Processing return invoice: {doc.name}, Return Against: {doc.return_against}")

        # Check if the return invoice was created from POS Awesome
        is_pos_invoice = frappe.db.get_value("Sales Invoice", doc.return_against, "is_pos")

        # Fetch original items from the parent invoice using SQL (bypasses permission restrictions)
        original_items = frappe.db.sql("""
            SELECT name, item_code, custom_is_returned FROM `tabSales Invoice Item`
            WHERE parent=%s
        """, (doc.return_against,), as_dict=True)

        original_items_dict = {item["item_code"]: item for item in original_items}
        frappe.logger().info(f"Original items from invoice {doc.return_against}: {original_items_dict}")

        for item in doc.items:
            if item.item_code in original_items_dict and item.qty < 0:
                item.custom_is_returned = 1  # Mark as returned in the return invoice
                frappe.logger().info(f"Item {item.item_code} marked as returned in return invoice.")

                # Also update the original invoice's item only if not already marked
                original_item = original_items_dict[item.item_code]
                if not original_item.get("custom_is_returned"):
                    frappe.db.set_value("Sales Invoice Item", original_item["name"], "custom_is_returned", 1)
                    frappe.logger().info(f"Item {item.item_code} marked as returned in original invoice.")

            else:
                item.custom_is_returned = 0  # Not returned in return invoice

        # Commit changes to ensure the database updates
        frappe.db.commit()



