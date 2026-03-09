# mappings.py

placements = {
    "TEXXEN TO CMS": {
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
                "date_column": "barcodeDate",
                "format": "%m-%d-%Y"
            },
            "Claim Paid Date": {                                 # <-- new conditional column
                "type": "if_gt_zero",
                "value_column": "Claim Paid Amount",
                "date_column": "barcodeDate",
                "format": "%m-%d-%Y"
            }
        }
    },
    "BPI CARDS XDAYS SL": {
        "header_mapping": {
            "CUST_ID": "accountNumber",
            "LAN": "accountNumber",
            "CH CODE": "chCode",
            "CH_CODE": "chCode",
            "CUST_NAME": "name",
            "NAME": "name",
            "BIRTHDATE": "birthday",
            "AOD": "ob",
            "PAYOFF AMOUNT": "ob",
            "PRINCIPAL": "principal",
            "ENDO DATE": "endoDate",
            "DATE REFERRED": "endoDate",
            "LAST DUE DATE": "cutOff",
            "CTL4": "placement",
            "UNIT_CODE": "productType",
            "DPD": "dpd",
            "QUEUE": "level",
            "TCL": "creditLimit",
            "MAD": "installmentAmount",
            "LAST PAYMENT AMOUNT": "lastPaymentAmount",
            "LAST_PAYMENT_DATE": "lastPaymentDate",
            "EMAIL": "email",
            "EMAIL_ALS": "email",
            "ADDRESS": "address1",
            "MOBILE_NO": "phone1",
            "MOBILE_ALS": "phone1",
            "HOME": "phone2",
            "MOBILE_ALFES": "phone2",
            "OFC": "phone3",
            "PRIMARY_NO_ALS": "phone3",
            "BUS_NO_ALS": "phone4",
            "LANDLINE_NO_ALS": "phone5"
        },
        "custom_fields": [
            "GENDER", "DELINQUENCY_STRING", "ADA_ACCOUNT",
            "DEBIT_AMOUNT_PREFERENCE", "HO FLAG",
            "BLOCK_CODE", "MEMO_LINE", "D_CUST_OPN", "PDA", "assignedAgent", "assignedTeam"
        ],
        "final_column_order": [
            "accountNumber", "accountNumber_2", "accountNumber_3",
            "cardNumber", "chCode", "name", "birthday", "ob", "newOb",
            "principal", "totalBalance", "endoDate", "cutOff",
            "placement", "productType", "cycle", "dpd", "level",
            "loanAmount", "creditLimit", "installmentAmount",
            "interest", "lastPaymentAmount", "lastPaymentDate",
            "writeOffAmount", "writeOffDate", "employer",
            "email", "address1", "address2", "address3",
            "address4", "address5",
            "phone1", "phone2", "phone3", "phone4", "phone5",
            "GENDER", "DELINQUENCY_STRING", "ADA_ACCOUNT",
            "DEBIT_AMOUNT_PREFERENCE", "HO FLAG",
            "BLOCK_CODE", "MEMO_LINE", "D_CUST_OPN", "PDA",
            "assignedAgent", "assignedTeam"
        ],
        "team_name": "BPI CARDS XDAYS SL TEAM 1",
        "cleaning": {
            "no_leading_zero_for_accountNumber": False   # default: add leading zero
        }
    },
    "BPI AUTO CURING SL": {
        "header_mapping": {
            "CUST_ID": "accountNumber",
            "LAN": "accountNumber",
            "CH CODE": "chCode",
            "CH_CODE": "chCode",
            "CUST_NAME": "name",
            "NAME": "name",
            "BIRTHDATE": "birthday",
            "AOD": "ob",
            "PAYOFF AMOUNT": "ob",
            "PRINCIPAL": "principal",
            "ENDO DATE": "endoDate",
            "DATE REFERRED": "endoDate",
            "LAST DUE DATE": "cutOff",
            "CTL4": "placement",
            "UNIT_CODE": "productType",
            "DPD": "dpd",
            "QUEUE": "level",
            "TCL": "creditLimit",
            "MAD": "installmentAmount",
            "LAST PAYMENT AMOUNT": "lastPaymentAmount",
            "LAST_PAYMENT_DATE": "lastPaymentDate",
            "EMAIL": "email",
            "EMAIL_ALS": "email",
            "ADDRESS": "address1",
            "MOBILE_NO": "phone1",
            "MOBILE_ALS": "phone1",
            "HOME": "phone2",
            "MOBILE_ALFES": "phone2",
            "OFC": "phone3",
            "PRIMARY_NO_ALS": "phone3",
            "BUS_NO_ALS": "phone4",
            "LANDLINE_NO_ALS": "phone5"
        },
        "custom_fields": [
            "PAST DUE", "UNIT", "LPC", "ADA SHORTAGE", "assignedAgent", "assignedTeam"
        ],
        "final_column_order": [
            "accountNumber", "accountNumber_2", "accountNumber_3",
            "cardNumber", "chCode", "name", "birthday", "ob", "newOb",
            "principal", "totalBalance", "endoDate", "cutOff",
            "placement", "productType", "cycle", "dpd", "level",
            "loanAmount", "creditLimit", "installmentAmount",
            "interest", "lastPaymentAmount", "lastPaymentDate",
            "writeOffAmount", "writeOffDate", "employer",
            "email", "address1", "address2", "address3",
            "address4", "address5",
            "phone1", "phone2", "phone3", "phone4", "phone5",
            "PAST DUE", "UNIT", "LPC", "ADA SHORTAGE",
            "assignedAgent", "assignedTeam"
        ],
        "team_name": "BPI AUTO CURING SL TEAM 1",
        "cleaning": {
            "no_leading_zero_for_accountNumber": True    # do NOT add leading zero
        }
    }
}