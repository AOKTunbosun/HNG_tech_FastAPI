

def single_string_palindrome_checker(str):
    return str == str[::-1]


def hash_string_sha256(str):
    import hashlib
    shas256_hash = hashlib.sha256()
    shas256_hash.update(str.encode('utf-8'))
    hex_digest = shas256_hash.hexdigest()
    return hex_digest
