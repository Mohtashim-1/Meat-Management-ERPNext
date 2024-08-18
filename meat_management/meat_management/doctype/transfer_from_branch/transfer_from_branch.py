# Copyright (c) 2024, mohtashim and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TransferFromBranch(Document):
	def validate(self):
		self.send_data()

	def send_data(self):
		if self.docstatus == 1:
			items = []
			for item in self.item:
				items.append({
					'item_code':item.item,
					'qty':item.qty
				})
			transfer_item = frappe.get_doc({
				'doctype':"Stock Entry",
				'stock_entry_type':"Material Receipt",
				'to_warehouse': self.warehouse,
				'items':items
			})
			transfer_item.insert(ignore_permissions=True)
			transfer_item.save()
			transfer_item.submit()

