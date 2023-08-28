import base64


def encode(string_to_encode):
    string = string_to_encode
    sample_string_bytes = string.encode("ascii")

    base64_bytes = base64.b64encode(sample_string_bytes)
    base64_string = base64_bytes.decode("ascii")
    return base64_string


def decode(string_to_decode):
    string = string_to_decode
    base64_bytes = string.encode("ascii")

    sample_string_bytes = base64.b64decode(base64_bytes)
    sample_string = sample_string_bytes.decode("ascii")
    return sample_string