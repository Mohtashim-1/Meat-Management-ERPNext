# Copyright (c) 2024, mohtashim and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StaffMeat(Document):
	def validate(self):
		self.data_to_bin()
		self.data_to_se()

	@frappe.whitelist()
	def get_data(self):
		rec = frappe.db.sql("""
			SELECT sd.employee_code FROM `tabStaff Detail` as sd
			WHERE sd.active = 1
			""", as_dict=1)
		if len(rec) > 0:
			self.data = []
		for r in rec:
			record_exists = frappe.db.exists(
            "Meat Staff Bin",
            {
                "employee_code": r['employee_code'],
                "period": self.period
            }
        )
			if not record_exists:
				self.append("data",{
					"employee_code":r.employee_code
				})
		self.save()
	
	def data_to_bin(self):
		if self.docstatus == 1:
			for item in self.data:
				bin = frappe.get_doc({
					"doctype":"Meat Staff Bin",
					"employee_code":item.employee_code,
					"active":item.active,
					"meat_provided":1,
					"period":self.period,
				})
				bin.insert(ignore_permissions=True)
				bin.save()
	
	def data_to_se(self):
		if self.docstatus == 1:
			se_items = []
			for item in self.data:
				if item.type:
					se_items.append({
						"item_code": item.type,
						"qty": item.qty
					})
		
			if se_items: 
				se = frappe.get_doc({
					"doctype": "Stock Entry",
					"stock_entry_type": "Material Issue",
					"from_warehouse": self.warehouse,
					"items": se_items
				})
				se.insert(ignore_permissions=True)
				se.save()
				se.submit()
			else:
				frappe.throw("No valid items to process.")


			
