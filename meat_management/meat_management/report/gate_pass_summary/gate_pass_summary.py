import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    columns = [
        {"label": "Gate Pass", "fieldname": "name", "fieldtype": "Link", "options": "Gate Pass", "width": 120},
        {"label": "Posting Date & Time", "fieldname": "posting_date_and_time", "fieldtype": "Datetime", "width": 160},
    ]

    party_type = filters.get("party_type", "").strip()

    if party_type == "Donor":
        columns.extend([
            {"label": "Donor Name", "fieldname": "donor_name", "fieldtype": "Data", "width": 120},
            {"label": "DN #", "fieldname": "dn_no", "fieldtype": "Data", "width": 120},
            {"label": "DN Branch", "fieldname": "branch", "fieldtype": "Data", "width": 120},
            {"label": "Category", "fieldname": "category", "fieldtype": "Data", "width": 100},
            {"label": "Total Qty", "fieldname": "total_qty", "fieldtype": "Float", "width": 100},
        ])
    elif party_type == "Saail":
        columns.extend([
            {"label": "Saail", "fieldname": "saail", "fieldtype": "Data", "width": 120},
            {"label": "Total Qty", "fieldname": "total_qty", "fieldtype": "Float", "width": 100},
        ])
    elif party_type == "Kitchen":
        columns.extend([
            {"label": "Tag No", "fieldname": "tag_no", "fieldtype": "Data", "width": 120},
            {"label": "Driver ID", "fieldname": "driver_id", "fieldtype": "Data", "width": 120},
            {"label": "Donor Name", "fieldname": "driver_name", "fieldtype": "Data", "width": 120},
            {"label": "Vehicle No", "fieldname": "vehicle_no", "fieldtype": "Data", "width": 120},
            {"label": "Total Qty", "fieldname": "total_qty", "fieldtype": "Float", "width": 100},
        ])
    else:
        columns.extend([
            {"label": "Saail", "fieldname": "saail", "fieldtype": "Data", "width": 120},
            {"label": "Slip No", "fieldname": "slip_no", "fieldtype": "Data", "width": 120},
            {"label": "C/O", "fieldname": "care_off", "fieldtype": "Data", "width": 120},
            {"label": "Total Qty", "fieldname": "total_qty", "fieldtype": "Float", "width": 100},
            
        ])

    return columns
def get_data(filters):
    conditions = []
    query_params = {}

    if filters.get("from_date"):
        conditions.append("posting_date_and_time >= %(from_date)s")
        query_params["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions.append("posting_date_and_time <= %(to_date)s")
        query_params["to_date"] = filters["to_date"]

    if filters.get("party_type"):
        # Clean up whitespace to avoid mismatches
        party_type = filters["party_type"].strip()
        query_params["party_type"] = party_type
        conditions.append("party_type = %(party_type)s")

    where_clause = " AND ".join(conditions)
    if where_clause:
        where_clause = "WHERE " + where_clause

    query = f"""
        SELECT 
            name, 
            posting_date_and_time, 
            party_type, 
            donor_name,
            saail,
            slip_no,
            care_off,
            kitchen, 
            total_qty, 
            vehicle_no, 
            driver_name
        FROM `tabGate Pass`
        {where_clause}
        ORDER BY posting_date_and_time DESC
    """

    # Uncomment to debug in logs if needed
    # frappe.log_error(f"Query Params: {query_params}", "Gate Pass Report")

    return frappe.db.sql(query, query_params, as_dict=True)
