import hmac
import hashlib
import binascii

# def macaroon_hmac_concat(key, data1, data2):
#     hash1 = hmac.new(
#         key,
#         msg=data1,
#         digestmod=hashlib.sha256
#     ).digest()
#     hash2 = hmac.new(
#         key,
#         msg=data2,
#         digestmod=hashlib.sha256
#     ).digest()
#     print(binascii.hexlify(hash1).decode('ascii'))
#     print(hash2)
#     combined = hash1 + hash2
#     print(combined)
#     return hmac.new(
#         key,
#         msg=combined.encode('ascii'),
#         digestmod=hashlib.sha256
#     ).hexdigest()



# macaroon_hmac_concat(b'\0','6b99edb2ec6d7a4382071d7d41a0bf7dfa27d87d2f9fea86e330d7850ffda2b2','82a80681f9f32d419af12f6a71787a1bac3ab199df934ed950ddf20c25ac8c65')

key = hmac.new(
            b'macaroons-key-generator',
            msg=b'\0',
            digestmod=hashlib.sha256
        ).digest()

key = ''

hash1 = hmac.new(
  key,
  msg='6b99edb2ec6d7a4382071d7d41a0bf7dfa27d87d2f9fea86e330d7850ffda2b2'.encode('ascii'),
  digestmod=hashlib.sha256
).digest()

print(hash1)
hexhash1 = binascii.hexlify(hash1)
print(hexhash1)

hash2 = hmac.new(
  key,
  msg='82a80681f9f32d419af12f6a71787a1bac3ab199df934ed950ddf20c25ac8c65'.encode('ascii'),
  digestmod=hashlib.sha256
).digest()
print(hash2)
hexhash2 = binascii.hexlify(hash2)
print(hexhash2)
combined = hash1 + hash2
print(combined)
hexcombined = hexhash1 + hexhash2
print(hexcombined)
hexlifiedcombined = binascii.hexlify(combined)
print(hexlifiedcombined)


combinehash = hmac.new(
  key,
  msg=hexlifiedcombined,
  digestmod=hashlib.sha256
).digest()

print(combinehash)

hexlifiedcombinedhash = binascii.hexlify(combinehash)
print(hexlifiedcombinedhash)


combinehash2 = hmac.new(
  key,
  msg=combined,
  digestmod=hashlib.sha256
).digest()

print(combinehash2)

hexlifiedcombinedhash2 = binascii.hexlify(combinehash2)
print(hexlifiedcombinedhash2)