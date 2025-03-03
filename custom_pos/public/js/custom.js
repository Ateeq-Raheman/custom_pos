// (function () {
//     console.log("🚀 Injecting POS Awesome Script...");

//     if (window.__pos_override_loaded) return;
//     window.__pos_override_loaded = true;

//     let original_frappe_call = frappe.call;

//     frappe.call = async function (options) {
//         console.log("📢 frappe.call intercepted:", options.method);

//         if (options.method === "posawesome.posawesome.api.posapp.search_invoices_for_return") {
//             console.log("🔍 Intercepting Invoice Search for Returns");

//             let original_callback = options.callback;

//             options.callback = async function (response) {
//                 console.log("📥 Original API Response:", response);

//                 if (response && response.message) {
//                     // Fetch all invoices that have a return entry
//                     let returned_invoices = await frappe.db.get_list("Sales Invoice", {
//                         fields: ["return_against"],
//                         filters: {
//                             "is_return": 1
//                         }
//                     });

//                     let returned_invoice_names = returned_invoices.map(inv => inv.return_against);

//                     // Filter invoices that have already been returned
//                     let filtered_invoices = response.message.filter(invoice => {
//                         console.log(`🔎 Checking Invoice: ${invoice.name}`);
//                         return !returned_invoice_names.includes(invoice.name);
//                     });

//                     console.log("✅ Filtered Invoices (Without Returns):", filtered_invoices);

//                     response.message = filtered_invoices;
//                 }

//                 if (original_callback) {
//                     console.log("📤 Sending Modified Data to UI");
//                     original_callback(response);
//                 }
//             };
//         }

//         return original_frappe_call.apply(this, arguments);
//     };

//     console.log("✅ POS Awesome Invoice Filter is Active");
// })();


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////




(function () {
    console.log("🚀 Injecting POS Awesome Script...");

    if (window.__pos_override_loaded) return;
    window.__pos_override_loaded = true;

    let original_frappe_call = frappe.call;

    frappe.call = async function (options) {
        console.log("📢 frappe.call intercepted:", options.method);

        if (options.method === "posawesome.posawesome.api.posapp.search_invoices_for_return") {
            console.log("🔍 Intercepting Invoice Search for Returns");

            let original_callback = options.callback;

            options.callback = async function (response) {
                console.log("📥 Original API Response:", response);

                if (response && response.message) {
                    console.log(`🔎 Received ${response.message.length} invoices to process.`);

                    let filtered_invoices = await Promise.all(response.message.map(async (invoice) => {
                        console.log(`📝 Fetching details for Invoice: ${invoice.name}`);

                        // Fetch full invoice details including items explicitly
                        let invoice_doc = await frappe.db.get_doc("Sales Invoice", invoice.name);

                        if (!invoice_doc || !invoice_doc.items || invoice_doc.items.length === 0) {
                            console.log(`⚠️ Invoice ${invoice.name} has no items. Skipping.`);
                            return null;
                        }

                        console.log(`✅ Invoice ${invoice.name} has ${invoice_doc.items.length} items.`);

                        // **Ensure we correctly read the checkbox value**
                        let non_returned_items = invoice_doc.items.filter(item => {
                            let isReturned = (item.custom_is_returned === 1 || item.custom_is_returned === true || item.custom_is_returned === "1");
                            console.log(`🔍 Checking Item: ${item.item_code} - Returned? ${isReturned}`);
                            return !isReturned;  // Only include items that are NOT returned
                        });

                        if (non_returned_items.length === 0) {
                            console.log(`❌ Invoice ${invoice.name} - All Items Returned. Skipping Invoice.`);
                            return null;
                        }

                        console.log(`✅ Invoice ${invoice.name} has ${non_returned_items.length} items left to return.`);

                        // Return the invoice with only non-returned items
                        let updated_invoice = { ...invoice, items: non_returned_items };
                        return updated_invoice;
                    }));

                    // Remove null values (fully returned invoices)
                    response.message = filtered_invoices.filter(inv => inv !== null);

                    console.log("📢 Final Filtered Invoices to Display:", response.message);

                    if (response.message.length === 0) {
                        console.warn("⚠️ No invoices found for return. Check item return statuses.");
                    }
                }

                if (original_callback) {
                    console.log("📤 Sending Modified Data to UI");
                    original_callback(response);
                }
            };
        }

        return original_frappe_call.apply(this, arguments);
    };

    console.log("✅ POS Awesome Invoice Filter is Active");
})();
