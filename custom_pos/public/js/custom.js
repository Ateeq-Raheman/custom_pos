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
                    // Fetch all invoices that have a return entry
                    let returned_invoices = await frappe.db.get_list("Sales Invoice", {
                        fields: ["name", "return_against"],
                        filters: {
                            "is_return": 1
                        }
                    });

                    let returned_invoice_names = returned_invoices.map(inv => inv.return_against);

                    // Fetch child table data for each invoice and check `custom_is_returned`
                    let invoices_to_keep = [];

                    for (let invoice of response.message) {
                        console.log(`🔎 Checking Invoice: ${invoice.name}`);

                        // Skip invoices that have been returned already
                        if (returned_invoice_names.includes(invoice.name)) {
                            continue;
                        }

                        // Fetch child items from the invoice
                        let invoice_items = await frappe.db.get_list("Sales Invoice Item", {
                            fields: ["custom_is_returned"],
                            filters: {
                                "parent": invoice.name
                            }
                        });

                        // Check if ALL items have `custom_is_returned` checked
                        let all_items_returned = invoice_items.every(item => item.custom_is_returned === 1);

                        if (!all_items_returned) {
                            invoices_to_keep.push(invoice);
                        }
                    }

                    console.log("✅ Filtered Invoices (Where Not All Items Are Returned):", invoices_to_keep);

                    response.message = invoices_to_keep;
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
