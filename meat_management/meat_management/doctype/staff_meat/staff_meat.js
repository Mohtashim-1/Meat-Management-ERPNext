// Copyright (c) 2024, mohtashim and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Staff Meat", {
// 	// refresh(frm) {

// 	// },
//     get_data(frm){
//         frm.call({
//             method:"get_data",
//             args:{

//             },
//             doc: frm.doc,
//             callback:function(r){
//                 frm.reload_doc()
//             }
//         })
//     }
// });

frappe.ui.form.on("Staff Meat", {
	get_data(frm) {
		frappe.call({
			method: "meat_management.meat_management.doctype.staff_meat.staff_meat.get_data",
			args: {
				doc: frm.doc
			},
			callback: function(r) {
				frm.reload_doc();
			}
		});
	}
});

