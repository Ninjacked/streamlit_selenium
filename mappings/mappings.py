# mappings.py

placements = {
    "TEXXEN TO CMS DRR": {
        "header_mapping": {
        "accountNumber": "Account No.",
        "accountName": "Debtor",
        "cardNumber": "Card No.",
        "dpd": "DPD",
        "notes": "Remark",
        "agent": ["Remark By", "Collector"],   # <-- list for two outputs
        "bankName": "Client",
        "ptpAmount": "PTP Amount",
        "paymentAmount": "Claim Paid Amount",
        "OB": "Balance",
        "cycle": "Cycle",
        "chCode": "Old IC",
        "status": "status",
        "substatus": "substatus",
        "startDate": "startDate",
        "endDate": "endDate",
        "barcodeDate": "barcodeDate"
        },
        "custom_fields": [
            "S.No","Service No.","Call Status","Product Description","Product Type",
            "Batch No","Account Type","Relation","Next Call","Dialed Number",
            "Days Past Write Off","Contact Type","I.C Issue Date","Bank Code",
            "Over Limit Amount","Min Payment","Due Date","Monthly Installment",
            "30 Days","MIA","Area","Call Duration","Talk Time Duration","Debtor ID",
            "Black Case No.","Red Case No.","Court Name","Lawyer","Legal Stage",
            "Legal Status","Next Legal Follow up"
        ],
        "final_column_order": [
            "S.No","Date","Time","Debtor","Account No.","Card No.","Service No.","DPD",
            "Call Status","Status","Remark","Remark By","Remark Type","Field Visit Date",
            "Collector","Client","Product Description","Product Type","Batch No",
            "Account Type","Relation","PTP Amount","PTP Date","Next Call",
            "Claim Paid Amount","Claim Paid Date","Dialed Number","Days Past Write Off",
            "Balance","Contact Type","Cycle","Old IC","I.C Issue Date","Bank Code",
            "Over Limit Amount","Min Payment","Due Date","Monthly Installment","30 Days",
            "MIA","Area","Call Duration","Talk Time Duration","Debtor ID",
            "Black Case No.","Red Case No.","Court Name","Lawyer","Legal Stage",
            "Legal Status","Next Legal Follow up","status","substatus","startDate",
            "endDate","barcodeDate"
        ],
        "team_name": "TEXXEN TO CMS DRR",
        "cleaning": {
            "no_leading_zero_for_accountNumber": True   # default: add leading zero
        },
        "computed_columns": {
            "Date": {
                "type": "date_format",
                "source": "barcodeDate",
                "format": "%m-%d-%Y"
            },
            "Time": {
                "type": "date_format",
                "source": "barcodeDate",
                "format": "%I:%M %p"
            },
            "Status": {
                "type": "concat",
                "sources": ["status", "substatus"],
                "separator": " - "
            },
            "PTP Date": {                                 # <-- new conditional column
                "type": "if_gt_zero",
                "value_column": "PTP Amount",
                "date_column": "endDate",
                "format": "%m-%d-%Y"
            },
            "Claim Paid Date": {                                 # <-- new conditional column
                "type": "if_gt_zero",
                "value_column": "Claim Paid Amount",
                "date_column": "endDate",
                "format": "%m-%d-%Y"
            }
        }
    },
    "CMS TO TEXXEN DRR": {
        "header_mapping": {
            "Account No.": "accountNumber",
            "Debtor": "accountName",
            "Card No.": "cardNumber",
            "DPD": "dpd",
            "Remark": "notes",
            "Remark By": "agent",  
            "Client": "bankName",
            "PTP Amount": "ptpAmount",
            "Claim Paid Amount": "paymentAmount",
            "Balance": "OB",
            "Cycle": "cycle",
            "Old IC": "chCode"
        },
        "custom_fields": [
            "_id","debtorId","principal"
        ],
        "final_column_order": [
            "S.No","Date","Time","Debtor","Account No.","Card No.","Service No.","DPD",
            "Call Status","Status","Remark","Remark By","Remark Type","Field Visit Date",
            "Collector","Client","Product Description","Product Type","Batch No",
            "Account Type","Relation","PTP Amount","PTP Date","Next Call",
            "Claim Paid Amount","Claim Paid Date","Dialed Number","Days Past Write Off",
            "Balance","Contact Type","Cycle","Old IC","I.C Issue Date","Bank Code",
            "Over Limit Amount","Min Payment","Due Date","Monthly Installment","30 Days",
            "MIA","Area","Call Duration","Talk Time Duration","Debtor ID",
            "Black Case No.","Red Case No.","Court Name","Lawyer","Legal Stage",
            "Legal Status","Next Legal Follow up","status","substatus","startDate",
            "endDate","barcodeDate"
        ],
        "team_name": "TEXXEN TO CMS DRR",
        "cleaning": {
            "no_leading_zero_for_accountNumber": True   # default: add leading zero
        },
        "computed_columns": {
            "Date": {
                "type": "date_format",
                "source": "barcodeDate",
                "format": "%m-%d-%Y"
            },
            "Time": {
                "type": "date_format",
                "source": "barcodeDate",
                "format": "%I:%M %p"
            },
            "Status": {
                "type": "concat",
                "sources": ["status", "substatus"],
                "separator": " - "
            },
            "PTP Date": {                                 # <-- new conditional column
                "type": "if_gt_zero",
                "value_column": "PTP Amount",
                "date_column": "endDate",
                "format": "%m-%d-%Y"
            },
            "Claim Paid Date": {                                 # <-- new conditional column
                "type": "if_gt_zero",
                "value_column": "Claim Paid Amount",
                "date_column": "endDate",
                "format": "%m-%d-%Y"
            }
        }
    }
}