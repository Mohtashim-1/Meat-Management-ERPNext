// Copyright (c) 2025, mohtashim and contributors
// For license information, please see license.txt

frappe.query_reports["Gate Pass Summary"] = {
	"filters": [
		{
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            default: frappe.datetime.add_days(frappe.datetime.get_today(), -7),
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1
        },
        {
			fieldname: "party_type",
			label: "Party Type",
			fieldtype: "Select",
			options: [
				"",
				"Donor",
				"Kitchen"
			]
		}
		
	]
};
