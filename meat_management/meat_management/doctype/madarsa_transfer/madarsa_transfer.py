# Copyright (c) 2024, mohtashim and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MadarsaTransfer(Document):
	def validate(self):
		self.calculate_total_qty()
		self.send_data()

	def calculate_total_qty(self):
		qty = 0
		for items in self.item:
			qty += items.qty
		self.total_qty = qty
	
	def send_data(self):
		if self.docstatus == 1:
			send_data_items = []
			for items in self.item:
				send_data_items.append({
					"item_code":items.item,
					"qty":items.qty
				})
			
			send_data = frappe.get_doc({
				"doctype" : "Stock Entry",
				"stock_entry_type": "Material Issue",
				"from_warehouse": self.warehouse,
				"items" : send_data_items
			})

			send_data.insert(ignore_permissions=True)
			send_data.save()
			send_data.submit()