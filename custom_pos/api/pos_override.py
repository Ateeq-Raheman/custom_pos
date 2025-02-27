# import frappe
# from frappe import _

# @frappe.whitelist()
# def search_invoices_for_return(txt="", start=0, page_len=20, filters=None):
#     filters = filters or {}

#     try:
#         frappe.logger().info("🔍 Fetching Sales Invoices for Return")

#         # Fetch all Sales Invoices (exclude returns)
#         invoices = frappe.get_all(
#             "Sales Invoice",
#             filters={"docstatus": 1, "is_return": 0},  
#             fields=["name", "customer", "posting_date", "total", "items"],
#             order_by="modified desc",
#             start=start,
#             page_length=page_len
#         )

#         frappe.logger().info(f"✅ Found {len(invoices)} non-return invoices.")

#         # If no invoices are found, return immediately
#         if not invoices:
#             frappe.logger().warning("⚠️ No invoices found in the database!")
#             return []

#         # Fetch all return invoices
#         returned_invoices = frappe.get_all(
#             "Sales Invoice",
#             filters={"is_return": 1},
#             fields=["return_against", "items"]
#         )

#         frappe.logger().info(f"🔄 Found {len(returned_invoices)} return invoices.")

#         # Create a mapping of returned items per invoice
#         returned_items_mapping = {}
#         for inv in returned_invoices:
#             if inv.return_against:
#                 try:
#                     returned_items_mapping.setdefault(inv.return_against, []).extend(
#                         [item["item_code"] for item in frappe.parse_json(inv.items) if "item_code" in item]
#                     )
#                 except Exception as e:
#                     frappe.logger().error(f"⚠️ Error parsing returned invoice items: {str(e)}")
#                     continue  

#         # Filter invoices based on returned items
#         filtered_invoices = []
#         for invoice in invoices:
#             try:
#                 original_items = frappe.parse_json(invoice["items"])
#             except Exception as e:
#                 frappe.logger().error(f"⚠️ Error parsing invoice items: {str(e)}")
#                 continue  

#             # Identify non-returned items
#             remaining_items = [
#                 item for item in original_items
#                 if invoice["name"] not in returned_items_mapping or item.get("item_code") not in returned_items_mapping[invoice["name"]]
#             ]

#             # ✅ Fix: Include invoices that have NEVER had a return
#             if invoice["name"] not in returned_items_mapping or remaining_items:
#                 invoice["items"] = remaining_items
#                 filtered_invoices.append(invoice)

#         frappe.logger().info(f"✅ Final Filtered Invoices Count: {len(filtered_invoices)}")

#         # Format results
#         results = [
#             [inv["name"], f"{inv['name']} - {inv['customer']} - {inv['posting_date']}"]
#             for inv in filtered_invoices
#         ]

#         return results

#     except Exception as e:
#         frappe.logger().error(f"❌ Error in search_invoices_for_return: {str(e)}")
#         return []
