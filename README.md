# Stripe-card-and-sk-checker


Description
This script provides a mechanism to automate interactions with the Stripe payment platform, particularly focusing on validating credit card details.

Core Features:
Secret Key Verification: The script first verifies the Stripe secret key (SK) to check its authenticity. This is done in two steps:

Using the Telethon library
Sending a GET request to Stripe's balance history endpoint.
Storing Secret Key: The secret key (SK) can be read from a file (sk.key). If not found, it prompts the user to enter the secret key and then saves it for future use.

Credit Card Processing: The main objective is to validate multiple credit card details, stored line by line in a specified file format (cc|mm|yy|cvv). The script processes each card by:

Creating a payment method for the card.
Registering a new customer using the payment method.
Attaching the payment method to the customer.
Attempting to make a charge (currently set to 100 USD) on the card. If the charge is successful, the card is marked as "live", otherwise "dead".
Saving Results: Live cards' details are saved to a separate file (live.txt).

Error Handling: The script contains comprehensive error-handling mechanisms. If Stripe responds with an error during any stage, it's displayed to the user. The error handling also considers specific card-related issues, such as insufficiency of funds or card expiration.

Refund: There's also a function for refunding a charge, although it's not currently utilized in the main execution flow.

How to Use:
The user provides a Stripe secret key either through the sk.key file or via input.
The user specifies a file containing credit card details in the format cc|mm|yy|cvv (credit card number, month, year, CVV).
The script then processes each card in the file, determining if they're "live" or "dead".
Cards that pass the charge test are written to the live.txt file.
Assumptions:
The secret key provided has the necessary permissions to carry out the described operations on Stripe.
The file containing credit card details is correctly formatted.
The user running the script understands the implications of attempting charges on multiple cards, which might be viewed as fraudulent behavior.
Please note: This kind of script, depending on its usage, can be illegal and unethical. Ensure you have permissions to perform operations on any card details you process. Always adhere to ethical guidelines and laws when dealing with sensitive information like credit card details.
