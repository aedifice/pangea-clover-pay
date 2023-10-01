import os
import clover

from clover import Token, Charge


# load sensitive Clover tokens
def clover_setup():
    clover.access_token = os.getenv("CLOVER_ACCESS_TOKEN")
    clover.api_key = os.getenv("CLOVER_PAKMS")


# return Clover-specific encryption information; since these are merchant-specific
# like our access token and API key, we've just stored this in env variables for now.
# If we expanded the app for multiple users/merchants, we could retrieve this info
# with the /v2/merchant/{mId}/pay/key endpoint.
def encrypt_info():
    return {
        "prefix": os.getenv("CLOVER_PREFIX"),
        "modulus": int(os.getenv("CLOVER_MODULUS")),
        "exponent": int(os.getenv("CLOVER_EXPONENT"))
    }


# Clover ecomm transactions require Clover card tokens; this tokenizes the card
def generate_card_token(card_number, encrypted_pan, exp_month, exp_year, cvv, zipcode):
    token = Token.create(
        card={
            "encrypted_pan": encrypted_pan,
            "exp_month": exp_month,
            "exp_year": exp_year,
            "cvv": cvv,
            "first6": card_number[:6],
            "last4": card_number[-4:],
            "address_zip": zipcode
        }
    )

    return token["id"]


# create a charge against a tokenized card for a specific amount; 
# returns success or failure
def create_charge(amount, token):
    charge = Charge.create(
        amount=int(amount)*100,  # convert dollars to cents
        currency="usd",
        source=token
    )

    if "id" in charge:
        # transaction succeeded (a new payment id was returned)
        return True
    return False
