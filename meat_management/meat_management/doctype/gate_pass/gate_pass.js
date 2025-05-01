// Copyright (c) 2025, mohtashim and contributors
// For license information, please see license.txt


frappe.ui.form.on("Gate Pass", {
    onload: function (frm) {
        frappe.call({
            method: "meat_management.meat_management.doctype.gate_pass.gate_pass.get_donor_dn_nos",  // Correct path
            callback: function (r) {
                if (r.message) {
                    let options = r.message.join("\n");  // Convert array of dn_no to options list
                    // Set options on the child table field
                    frm.fields_dict.gate_pass_item.grid.get_field("dn_no").df.options = options;
                    frm.fields_dict.gate_pass_item.grid.refresh();
                }
            }
        });
    }
});
    