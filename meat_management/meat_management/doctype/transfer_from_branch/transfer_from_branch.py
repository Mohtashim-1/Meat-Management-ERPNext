# Copyright (c) 2024, mohtashim and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TransferFromBranch(Document):
    def validate(self):
        self.send_data()
        self.transfer_branch_to_slaughter()

    def send_data(self):
        bn = frappe.get_doc("Branch Name", self.branch)
        br_w = bn.warehouse
        if self.docstatus == 1:
            items = []
            for item in self.item:
                items.append({
                    'item_code': item.item,
                    'qty': item.qty
                })
            transfer_item = frappe.get_doc({
                'doctype': "Stock Entry",
                'stock_entry_type': "Material Receipt",
                'to_warehouse': br_w,
                'items': items
            })
            transfer_item.insert(ignore_permissions=True)
            transfer_item.submit()

    def transfer_branch_to_slaughter(self):
        bn = frappe.get_doc("Branch Name", self.branch)
        br_w = bn.warehouse
        sl = frappe.get_doc("Slaughter", self.slaughter)
        sl_w = sl.warehouse
        if self.docstatus == 1:
            items = []
            for item in self.item:
                items.append({
                    'item_code': item.item,
                    'qty': item.qty
                })
            transfer_item = frappe.get_doc({
                'doctype': "Stock Entry",
                'stock_entry_type': "Material Transfer",
                'from_warehouse': br_w,
                'to_warehouse': sl_w,
                'items': items
            })
            transfer_item.insert(ignore_permissions=True)
            transfer_item.submit()
