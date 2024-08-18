# Copyright (c) 2024, mohtashim and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import frappe.utils


class StaffMeat(Document):
	def validate(self):
		self.data_to_bin()
		self.data_to_se()
		self.check_period()

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
	
	def check_period(self):
		try:
			doc = frappe.get_doc("Staff Meat", self.name)
			meat_period = frappe.get_doc("Meat Period", doc.period)
			meat_period_start = meat_period.from_date
			if meat_period_start:
				posting_date = self.posting_date
				if isinstance(posting_date, str):
					posting_date = frappe.utils.getdate(posting_date)
				
				if posting_date < meat_period_start:
					frappe.throw(f"Posting date {posting_date} cannot be earlier than the period start date {meat_period_start}")

			meat_period_end = meat_period.to_date
			if meat_period_end:
				posting_date = self.posting_date
				if isinstance(posting_date, str):
					posting_date = frappe.utils.getdate(posting_date)
				
				if posting_date > meat_period_end:
					frappe.throw(f"Posting date {posting_date} cannot be greater than the period End date {meat_period_start}")

				
				
		except frappe.DoesNotExistError as e:
			frappe.msgprint(f"Document not found: {e}")
		except Exception as e:
			frappe.msgprint(f"Error occurred: {e}")
