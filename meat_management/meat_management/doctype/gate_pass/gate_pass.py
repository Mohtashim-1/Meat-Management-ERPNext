# Copyright (c) 2025, mohtashim and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class GatePass(Document):
    def validate(self):
        self.send_data()
        self.check_duplicate_reference()
        self.calculate_total_qty()

    def calculate_total_qty(self):
        total = 0.0
        for item in self.gate_pass_item:
            total += float(item.qty or 0)
        self.total_qty = total


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

@frappe.whitelist()
def get_donor_dn_nos():
    dn_nos = frappe.get_all(
        "Donor Detail",
        filters={"dn_no": ["!=", ""]},
        fields=["dn_no"]
    )
    # Extract and return unique non-empty dn_no
    return list(set(d["dn_no"] for d in dn_nos if d["dn_no"]))