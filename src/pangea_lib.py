import base64
import os

from pangea.config import PangeaConfig
from pangea.services import Audit, Vault
from pangea.services.vault.models.asymmetric import AsymmetricAlgorithm
from pangea.services.vault.models.common import KeyPurpose


# set up Pangea configuration based on env variables
audit_token = os.getenv("PANGEA_AUDIT_TOKEN")
vault_token = os.getenv("PANGEA_VAULT_TOKEN")
domain = os.getenv("PANGEA_DOMAIN")
config = PangeaConfig(domain=domain)
audit = Audit(audit_token, config=config)
vault = Vault(vault_token, config=config)


# create a new encryption key with a given name
def generate_encryption_key(name):
    response = vault.asymmetric_generate(
        name=name,
        algorithm=AsymmetricAlgorithm.RSA2048_OAEP_SHA1,
        purpose=KeyPurpose.ENCRYPTION
    )

    # pull out id and public key from result; we currently only use the id to
    # access this key again later, but public key could be useful to have
    return { "id": response.result.id, "public_key": response.result.public_key }


# encrypt a string using a given Pangea encryption key id
def encrypt_string(key_id, value):
    # string must be base64-encoded first
    encoded_str = base64.b64encode(value.encode())
    response = vault.encrypt(key_id, encoded_str)
    return { "id": response.result.id, "cipher_text": response.result.cipher_text }


# decrypt cipher text based on a specific Pangea encryption key id
def decrypt_string(key_id, cipher_text):
    response = vault.decrypt(key_id, cipher_text)
    encoded_text = response.result.plain_text
    # undo base64 encoding and back to regular utf-8 instead of a byte string
    plain_text = base64.b64decode(encoded_text).decode("utf-8")

    return plain_text


# save a message to the secure audit log
# we use this to save transaction results so we can review for charge amounts
# and suspicious activity
def save_audit_log(message):
    audit.log(message=message)
