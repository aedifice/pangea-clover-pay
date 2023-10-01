import base64
import uuid
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from flask import session

from clover_lib import (
    clover_setup, generate_card_token, create_charge, encrypt_info
)
from pangea_lib import (
    generate_encryption_key, encrypt_string, decrypt_string, save_audit_log
)


clover_setup()

# construct a public RSA key specific to the Clover merchant to encrypt the card
def encrypt_pan(card):
    info = encrypt_info()
    rsaKey = RSA.construct((info["modulus"], info["exponent"]))
    cipher = PKCS1_OAEP.new(rsaKey)

    encrypted_pan = base64.b64encode(cipher.encrypt((info["prefix"] + card).encode()))
    return encrypted_pan


# undo Pangea encryption to unpack card details from stored session
def decrypt_saved_card():
    key_id = session["card"]["id"]
    encrypted_card = session["card"]["cipher_text"]
    decrypted_string = decrypt_string(key_id, encrypted_card)
    decrypted_card = decrypted_string.split("|")

    return {
        "card": decrypted_card[0],
        "expiration": decrypted_card[1],
        "cvv": decrypted_card[2],
        "zipcode": decrypted_card[3]
    }


# put together a message about the transaction attempt to log with Pangea;
# the audit log can be reviewed for suspicious activity like transactions with the
# same card or many failures in a row
def pay_log(amount, last4, success):
    success_msg = "failed"
    if success:
        success_msg = "made"
    
    message = f"Payment for ${amount} {success_msg} using card ending in {last4}"
    save_audit_log(message)


# attempt a transaction and return whether it succeeded or not
def charge_request(amount, card, expiration, cvv, zipcode, save):
    # if we have a request to save the card, encrypt details with Pangea before
    # saving the encrypted card to the session
    if save:
        card_details = f"{card}|{expiration}|{cvv}|{zipcode}"
        # generate a unique name for the new encryption key
        key_info = generate_encryption_key(f"clv-{uuid.uuid4()}")
        encrypted_details = encrypt_string(key_info["id"], card_details)

        session["card"] = encrypted_details

    # lazy MM/YY processing for demo purposes, but this should really have validation
    exp = expiration.split("/")
    encrypted_pan = encrypt_pan(card).decode("utf-8")

    # generate a Clover card token and submit a charge against it
    success = False
    try:
        token = generate_card_token(card, encrypted_pan, exp[0], exp[1], cvv, zipcode)
        success = create_charge(amount, token)
    except:
        # an exception shouldn't break the app, and success will remain False
        pass

    pay_log(amount, card[-4:], success)
    return success
