frappe.pages['posapp'].on_page_load = function (wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'POS Awesome',
        single_column: true
    });

    // Override return invoice search
    frappe.posawesome.search_invoices_for_return = function (search_term, callback) {
        frappe.call({
            method: "custom_pos.api.pos_override.search_invoices_for_return",
            args: {
                txt: search_term || "",
                start: 0,
                page_len: 20,
                filters: {}
            },
            callback: function (response) {
                if (response.message) {
                    callback(response.message);
                } else {
                    callback([]);
                }
            }
        });
    };
};
