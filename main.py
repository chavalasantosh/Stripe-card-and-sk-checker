import requests
import os
import stripe


def verify_sk_module(api_key):
    try:
        stripe.api_key = api_key
        stripe.Account.retrieve()
        return True
    except stripe.error.InvalidRequestError:
        return False

def verify_sk(sk):
    if not verify_sk_module(sk):
        return False

    HEADERS = {
        'Authorization': 'Bearer ' + sk,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    ENDPOINT = "https://api.stripe.com/v1/balance/history"
    
    response = requests.get(ENDPOINT, headers=HEADERS)
    
    if response.status_code == 200:
        result = response.json()
        if 'data' in result and isinstance(result['data'], list):
            for transaction in result['data']:
                print("Transaction ID:", transaction.get('id'))
                print("Amount:", transaction.get('amount'))
                print("Currency:", transaction.get('currency'))
                print("Status:", transaction.get('status'))
                print("Type:", transaction.get('type'))
                print("Description:", transaction.get('description') or "N/A")
                print("------------------------")
        return True
    else:
        error_msg = handle_stripe_error(response.json())
        print(f"Error verifying Secret Key: {error_msg}")
        return False

def get_auth():
    if os.path.exists("sk.key"):
        with open("sk.key", "r") as file:
            return file.read().strip()
    return None

def save_auth(SK):
    with open("sk.key", "w") as file:
        file.write(SK)

def create_payment_method(cc, mm, yy, cvv, sk):
    HEADERS = {
        'Authorization': 'Bearer ' + sk,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    ENDPOINT = "https://api.stripe.com/v1/payment_methods"
    data = {
        'type': 'card',
        'card[number]': cc,
        'card[exp_month]': mm,
        'card[exp_year]': yy,
        'card[cvc]': cvv
    }

    response = requests.post(ENDPOINT, data=data, headers=HEADERS)
    result = response.json()

    if response.status_code == 200:
        return result.get('id')
    else:
        error_msg = handle_stripe_error(result)
        print(f"Error with card ending in {cc[-4:]}: {error_msg}")
        return None

def refund_charge(charge_id, sk):
    HEADERS = {
        'Authorization': 'Bearer ' + sk,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    ENDPOINT = f"https://api.stripe.com/v1/refunds"
    data = {
        "charge": charge_id
    }

    response = requests.post(ENDPOINT, data=data, headers=HEADERS)
    result = response.json()
    
    if response.status_code == 200:
        print(f"Successfully refunded charge {charge_id}.")
    else:
        print(f"Failed to refund charge {charge_id}. Reason: {result.get('error', {}).get('message', 'Error during refund')}")
        
def create_customer(payment_method_id, sk):
    HEADERS = {
        'Authorization': 'Bearer ' + sk,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    ENDPOINT = "https://api.stripe.com/v1/customers"
    data = {
        "payment_method": payment_method_id
    }

    response = requests.post(ENDPOINT, data=data, headers=HEADERS)
    result = response.json()
    
    if response.status_code == 200:
        return result.get('id')
    else:
        error_msg = handle_stripe_error(result)
        print(f"Error creating customer with payment method {payment_method_id}. Reason: {result.get('error', {}).get('message', 'Unknown error')}")
        return None


def attach_payment_method_to_customer(payment_method_id, customer_id, sk):
    HEADERS = {
        'Authorization': 'Bearer ' + sk,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    ENDPOINT = f"https://api.stripe.com/v1/payment_methods/{payment_method_id}/attach"
    data = {
        "customer": customer_id
    }

    response = requests.post(ENDPOINT, data=data, headers=HEADERS)
    result = response.json()

    if response.status_code == 200:
        return True
    else:
        print(f"Failed to attach payment method {payment_method_id} to customer {customer_id}. Reason: {result.get('error', {}).get('message', 'Unknown error')}")
        return False
    

def attempt_charge(payment_method_id, customer_id, sk):
    HEADERS = {
        'Authorization': 'Bearer ' + sk,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    CHARGE_ENDPOINT = "https://api.stripe.com/v1/charges"
    data = {
        "amount": 100,  # This is a placeholder; adjust as needed.
        "currency": "usd",  
        "payment_method": payment_method_id,
        "customer": customer_id,
        # Add any other necessary fields.
    }

    response = requests.post(CHARGE_ENDPOINT, data=data, headers=HEADERS)
    result = response.json()

    if response.status_code == 200:
        return True, result.get('id')
    else:
        return False, None

def handle_stripe_error(result):
    error_type = result.get('error', {}).get('type')
    error_message = result.get('error', {}).get('message', 'Unknown error')
    
    if error_type == "card_error":
        card_err_code = result.get('error', {}).get('code')
        
        if card_err_code == "insufficient_funds":
            return "The card has insufficient funds."
        elif card_err_code == "card_declined":
            return "The card was declined."
        elif card_err_code == "expired_card":
            return "The card has expired."
        else:
            return f"Card Error: {error_message}"
    else:
        return error_message

if __name__ == "__main__":
    SK = get_auth()
    
    if not SK:
        SK = input("SK [$]: - ")
        save_auth(SK)

    if not verify_sk(SK):
        print("The provided Secret Key is not valid.")
        exit(1)

    filename = input("[+] Enter your file : ")

    with open(filename, 'r') as file:
        CClist = file.read().splitlines()

    for i in CClist:
        cc, mm, yy, cvv = i.split('|')
        payment_method_id = create_payment_method(cc, mm, yy, cvv, SK)
        
        if payment_method_id:
            customer_id = create_customer(payment_method_id, SK)
            
            if customer_id:
                attached = attach_payment_method_to_customer(payment_method_id, customer_id, SK)
                
                if attached:
                    is_live, charge_id = attempt_charge(payment_method_id, customer_id, SK)
                    
                    if is_live:
                        message=(f"Card ending in {cc[-4:]} is live.")
                        print(message)

                        if not os.path.exists('live.txt'):
                            with open('live.txt', 'w') as file:
                                file.write(message + '\n')
                        else:
                            with open('live.txt', 'a') as file:
                                file.write(message + '\n')
                        
                    else:
                        print(f"Card ending in {cc[-4:]} is dead.")
                else:
                    print(f"Failed to attach card ending in {cc[-4:]} to customer.")
            else:
                print(f"Failed to authenticate card ending in {cc[-4:]}")
        else:
            print(f"Failed to create payment method for card ending in {cc[-4:]}")
