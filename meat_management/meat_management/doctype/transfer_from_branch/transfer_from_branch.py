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

    bn = frappe.get_doc("Branch Name", doc.branch)
    br_w = bn.warehouse

    # --- Step 1: Material Issue (raw items from branch) ---
    issue_items = []
    for item in doc.item:
        issue_items.append({
            'item_code': item.item,
            'qty': item.qty,
            'uom': item.uom,  # Assuming uom is available on the child table
            's_warehouse': sl_w
        })

    stock_issue = frappe.get_doc({
        'doctype': "Stock Entry",
        'stock_entry_type': "Material Issue",
        'items': issue_items
    })
    stock_issue.insert(ignore_permissions=True)
    stock_issue.submit()

    # --- Step 2: Material Receipt (processed parts to slaughter) ---
    receipt_items = []

    for i in doc.item:
        item_code = i.item
        item_qty = i.qty

        item_doc = frappe.get_doc("Item", item_code)
        item_parts = item_doc.get("custom_item_part")

        for part in item_parts:
            item_part_item = part.parts
            item_part_qty = part.quantity * item_qty
            item_part_uom = part.uom

            receipt_items.append({
                "item_code": item_part_item,
                "qty": item_part_qty,
                "uom": item_part_uom,
                "t_warehouse": sl_w
            })

    stock_receipt = frappe.get_doc({
        'doctype': "Stock Entry",
        'stock_entry_type': "Material Receipt",
        'items': receipt_items
    })
    stock_receipt.insert(ignore_permissions=True)
    stock_receipt.submit()

    return {"status": "success", "message": "Slaughter operation created successfully"}
