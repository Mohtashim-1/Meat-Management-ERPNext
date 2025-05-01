# Copyright (c) 2025, mohtashim and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class GatePass(Document):
    def validate(self):
        self.send_data()
        self.check_duplicate_reference()

    def send_data(self):
        bn = frappe.get_doc("Slaughter", self.slaughter)
        br_w = bn.warehouse
        if self.docstatus == 1:
            items = []
            for item in self.gate_pass_item:
                items.append({
                    'item_code': item.item,
                    'qty': item.qty,
                    'uom': item.uom,
                    's_warehouse': br_w
                })
            transfer_item = frappe.get_doc({
                'doctype': "Stock Entry",
                'stock_entry_type': "Material Issue",
                's_warehouse': br_w,
                'items': items
            })
            transfer_item.insert(ignore_permissions=True)
            transfer_item.submit()

    def check_duplicate_reference(self):
        if self.slip_no:
            duplicate = frappe.db.exists("Gate Pass", {
                "slip_no": self.slip_no,
                "name": ["!=", self.name]
            })
            if duplicate:
                frappe.throw(_("Reference Number {0} is already used in Gate Pass {1}. It could not been duplicated.")
                             .format(self.slip_no, duplicate))
