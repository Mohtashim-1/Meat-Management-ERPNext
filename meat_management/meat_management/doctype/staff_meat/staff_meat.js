// Copyright (c) 2024, mohtashim and contributors
// For license information, please see license.txt

frappe.ui.form.on("Staff Meat", {
	// refresh(frm) {

	// },
    get_data(frm){
        frm.call({
            method:"get_data",
            args:{

            },
            doc: frm.doc,
            callback:function(r){
                frm.reload_doc()
            }
        })
    }
});
