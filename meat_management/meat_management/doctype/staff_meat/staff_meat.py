# Copyright (c) 2024, mohtashim and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import frappe.utils
import json


class StaffMeat(Document):
	def validate(self):
		self.data_to_bin()
		self.data_to_se()
		# self.check_period()
		self.check_15_day_gap()

	

	
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


	def check_15_day_gap(self):
		for row in self.data:
			last_entry = frappe.db.sql("""
				SELECT posting_date FROM `tabStaff Meat`
				JOIN `tabStaff Meat CT` ON `tabStaff Meat`.name = `tabStaff Meat CT`.parent
				WHERE `tabStaff Meat CT`.employee_code = %s
				AND `tabStaff Meat`.docstatus = 1
				AND `tabStaff Meat`.name != %s
				ORDER BY `tabStaff Meat`.posting_date DESC
				LIMIT 1
			""", (row.employee_code, self.name), as_dict=True)

			if last_entry:
				last_date = last_entry[0].posting_date
				current_date = frappe.utils.getdate(self.posting_date)
				days_difference = (current_date - last_date).days

				if days_difference < 15:
					next_date = frappe.utils.add_days(last_date, 15)
					frappe.throw(
						f"Employee {row.employee_code} already received meat on {frappe.utils.formatdate(last_date, 'dd-MM-yyyy')}. "
						f"Next eligible date: {frappe.utils.formatdate(next_date, 'dd-MM-yyyy')}. Must wait {15 - days_difference} more day(s)."
					)


@frappe.whitelist()
def get_data(doc):
	doc = frappe.get_doc(json.loads(doc))

	staff = frappe.db.get_all(
		"Staff Detail",
		filters={"active": 1},
		fields=["employee_code", "name1", "department", "incharge", "salary", "active"]
	)

	doc.data = []

	for s in staff:
		already_received = frappe.db.exists("Meat Staff Bin", {
			"employee_code": s.employee_code,
			"period": doc.period
		})
		if not already_received:
			doc.append("data", {
				"employee_code": s.employee_code,
				"name1": s.name1,
				"department": s.department,
				"incharge": s.incharge,
				"salary": s.salary,
				"active": s.active,
				"qty": 1.5  # default if you want to auto-fill
			})

	doc.save()
	return "done"
