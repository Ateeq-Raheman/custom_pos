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



/////////////////////////////////////////////////////////////////////////////////////////////////////////////


(function () {
    console.log("🚀 Injecting POS Awesome Script...");

    if (window.__pos_override_loaded) return;
    window.__pos_override_loaded = true;

    let original_frappe_call = frappe.call;

    frappe.call = async function (options) {
        console.log("📢 frappe.call intercepted:", options.method);

        // Step 1: Intercept Return Submission
        if (options.method === "frappe.client.insert" && options.args.doctype === "Sales Invoice") {
            console.log("🔄 Intercepting Sales Invoice Submission for Returns");

            let original_callback = options.callback;

            options.callback = async function (response) {
                console.log("📥 Return Invoice Created:", response);

                if (response && response.message && response.message.is_return) {
                    let return_invoice = response.message;
                    console.log("🔍 Checking returned items for update...");

                    // Step 2: Identify Items Being Returned
                    let return_items = return_invoice.items.map(item => ({
                        item_code: item.item_code,
                        original_invoice: item.return_against,
                        qty: item.qty
                    }));

                    for (let item of return_items) {
                        console.log(`🔄 Marking item as returned: ${item.item_code} in ${item.original_invoice}`);

                        // Step 3: Update custom_is_returned in the Original Invoice's Items
                        await frappe.db.update("Sales Invoice Item", {
                            filters: {
                                parent: item.original_invoice,
                                item_code: item.item_code
                            },
                            fieldname: "custom_is_returned",
                            value: 1
                        });
                    }

                    console.log("✅ Return items updated successfully.");
                }

                if (original_callback) {
                    console.log("📤 Sending Response to UI");
                    original_callback(response);
                }
            };
        }

        // Step 4: Modify Invoice Search to Hide Returned Items
        if (options.method === "posawesome.posawesome.api.posapp.search_invoices_for_return") {
            console.log("🔍 Intercepting Invoice Search for Returns");

            let original_callback = options.callback;

            options.callback = async function (response) {
                console.log("📥 Original API Response:", response);

                if (response && response.message) {
                    // Fetch invoices with return entries
                    let returned_invoices = await frappe.db.get_list("Sales Invoice", {
                        fields: ["name"],
                        filters: {
                            "is_return": 1
                        }
                    });

                    let returned_invoice_names = returned_invoices.map(inv => inv.name);

                    // Process invoices individually
                    let filtered_invoices = await Promise.all(response.message.map(async (invoice) => {
                        console.log(`🔎 Checking Invoice: ${invoice.name}`);

                        // Fetch invoice items
                        let invoice_items = await frappe.db.get_list("Sales Invoice Item", {
                            fields: ["item_code", "custom_is_returned"],
                            filters: {
                                "parent": invoice.name
                            }
                        });

                        // Filter out returned items
                        let non_returned_items = invoice_items.filter(item => !item.custom_is_returned);

                        if (non_returned_items.length > 0) {
                            console.log(`✅ Invoice ${invoice.name} has ${non_returned_items.length} non-returned items.`);
                            invoice.items = non_returned_items; // Keep only non-returned items
                            return invoice;
                        } else {
                            console.log(`❌ Invoice ${invoice.name} is fully returned and will be removed.`);
                            return null;
                        }
                    }));

                    // Remove null values (fully returned invoices)
                    response.message = filtered_invoices.filter(invoice => invoice !== null);

                    console.log("✅ Filtered Invoices (Without Fully Returned Items):", response.message);
                }

                if (original_callback) {
                    console.log("📤 Sending Modified Data to UI");
                    original_callback(response);
                }
            };
        }

        return original_frappe_call.apply(this, arguments);
    };

    console.log("✅ POS Awesome Return Update & Filtering Active");
})();
