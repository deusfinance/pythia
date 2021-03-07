from eth_account import Account, messages


def sign(private_key, text):
    message = messages.encode_defunct(text=text)
    signed_message = Account.sign_message(message, private_key=private_key)
    return signed_message.signature.hex()


def recover(message, signature):
    # print("crypto.recover", message, signature)
    message = messages.encode_defunct(text=message)
    address = Account.recover_message(message, signature=signature)
    return address
