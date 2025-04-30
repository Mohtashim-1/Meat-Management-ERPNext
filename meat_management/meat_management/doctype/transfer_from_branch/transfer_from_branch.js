// Copyright (c) 2024, mohtashim and contributors
// For license information, please see license.txt


frappe.ui.form.on("Transfer From Branch", {
	refresh(frm) {
		// Show button only after saving (docstatus == 1)
		if (!frm.is_new() && frm.doc.docstatus === 1) {
			frm.add_custom_button("Create Slaughter Operation", function () {
				frappe.call({
					method: "meat_management.meat_management.doctype.transfer_from_branch.transfer_from_branch.create_slaughter_operation",
					args: {
						docname: frm.doc.name
					},
					callback: function (r) {
						if (!r.exc) {
							frappe.msgprint("Slaughter Operation created successfully");
							frm.reload_doc();
						}
					}
				});
			});
		}
	}
});

