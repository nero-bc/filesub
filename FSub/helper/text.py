import base64


def str_encoder(string):
    string_bytes  = string.encode("ascii")
    base64_bytes  = base64.urlsafe_b64encode(string_bytes)
    base64_string = (base64_bytes.decode("ascii")).strip("=")
    return base64_string


def str_decoder(base64_string):
    base64_string = base64_string.strip("=")
    base64_bytes  = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes  = base64.urlsafe_b64decode(base64_bytes) 
    decode_string = string_bytes.decode("ascii")
    return decode_string