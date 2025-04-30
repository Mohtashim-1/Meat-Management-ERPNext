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
            
@frappe.whitelist()
def create_slaughter_operation(docname):
    
    doc = frappe.get_doc("Transfer From Branch", docname)
    sl = frappe.get_doc("Slaughter", doc.slaughter)
    sl_w = sl.warehouse
    
    for i in doc.item:
        item_code = i.item
        item_qty = i.qty

        # Get the original item and its custom item parts
        item_doc = frappe.get_doc("Item", item_code)
        item_parts = item_doc.get("custom_item_part")  # assuming this is the child table fieldname

        for part in item_parts:
            item_part_item = part.parts
            item_part_qty = part.quantity * item_qty  # multiply by qty of main item
            item_part_uom = part.uom

            # Create Stock Entry for each part (Material Request or Material Issue)
            stock_entry = frappe.get_doc({
                "doctype": "Stock Entry",
                "stock_entry_type": "Material Receipt",
                "items": [{
                    "item_code": item_part_item,
                    "qty": item_part_qty,
                    "uom": item_part_uom,
                    't_warehouse': sl_w  # you may need to set this on your DocType
                }]
            })
            stock_entry.insert(ignore_permissions=True)
            stock_entry.submit()

    return {"status": "success", "message": "Slaughter operation created successfully"}
