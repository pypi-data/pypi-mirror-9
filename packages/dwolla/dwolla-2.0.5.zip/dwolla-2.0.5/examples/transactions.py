'''
      _               _ _
   __| |_      _____ | | | __ _
  / _` \ \ /\ / / _ \| | |/ _` |
 | (_| |\ V  V / (_) | | | (_| |
  \__,_| \_/\_/ \___/|_|_|\__,_|

  An official requests based wrapper for the Dwolla API.

  The following is a quick-start example for the transaction endpoints.
'''

from dwolla import transactions, constants

# Configure the library (change these)
constants.sandbox=False

constants.client_id = "zbDwIC0dWCVU7cQtfvGwVwVjvxwQfjaTgkVi+FZOmKqPBzK5JG"
constants.client_secret = "ckmgwJz9h/fZ09unyXxpupCyrmAMe0bnUiMHF/0+SDaR9RHe99"
constants.access_token = "aK6DdCVlIsR1hKvTbp8VCwnvci8cwaTLlW9edtbHJVmKoopnoe"
constants.pin = 1234

# Example 1: Send $5.50 to a Dwolla ID.

print(transactions.send('812-197-4121', 5.50))
# Return:
# 113533 (Sender's transaction ID)


# Example 2: List transactions for the user
# associated with the current OAuth token.

print(transactions.get())
# Return:
# [
#     {
#         "Id": 113533,
#         "Amount": 5.50,
#         "Date": "2014-12-13T05:07:15Z",
#         "Type": "money_sent",
#         "UserType": "Email",
#         "DestinationId": "812-197-4121",
#         "DestinationName": "Some Name",
#         "Destination": {
#             "Id": "812-197-4121",
#             "Name": "Some Name",
#             "Type": "dwolla",
#             "Image": ""
#         },
#         "SourceId": "812-202-3784",
#         "SourceName": "David Stancu",
#         "Source": {
#             "Id": "812-202-3784",
#             "Name": "David Stancu",
#             "Type": "Dwolla",
#             "Image": "https://dwolla-avatars.s3.amazonaws.com/812-202-3784/ac045522"
#         },
#         "ClearingDate": "",
#         "Status": "cancelled",
#         "Notes": "",
#         "Fees": null,
#         "OriginalTransactionId": null,
#         "Metadata": null
#     },
#     ...
# ]

# Example 3: Refund $2 from "Balance" from transaction
# '123456'

print(transactions.refund('3452346', 'Balance', 2.00))
# Return:
# {
#     "TransactionId": 4532,
#     "RefundDate": "2014-12-10T12:01:09Z",
#     "Amount": 2.00
# }


# Example 4: Get info for transaction ID '123456'.

print(transactions.info('113533'))
# Return:
#     {
#         "Id": 113533,
#         "Amount": 5.50,
#         "Date": "2014-12-13T05:07:15Z",
#         "Type": "money_sent",
#         "UserType": "Email",
#         "DestinationId": "812-197-4121",
#         "DestinationName": "Some Name",
#         "Destination": {
#             "Id": "812-197-4121",
#             "Name": "Some Name",
#             "Type": "dwolla",
#             "Image": ""
#         },
#         "SourceId": "812-202-3784",
#         "SourceName": "David Stancu",
#         "Source": {
#             "Id": "812-202-3784",
#             "Name": "David Stancu",
#             "Type": "Dwolla",
#             "Image": "https://dwolla-avatars.s3.amazonaws.com/812-202-3784/ac045522"
#         },
#         "ClearingDate": "",
#         "Status": "cancelled",
#         "Notes": "",
#         "Fees": null,
#         "OriginalTransactionId": null,
#         "Metadata": null
#     }


# Example 5: Get transaction statistics for the user
# associated with the current OAuth token.

print(transactions.stats())
# Return:
# {
#     "TransactionsCount": 5,
#     "TransactionsTotal": 116.92
# }