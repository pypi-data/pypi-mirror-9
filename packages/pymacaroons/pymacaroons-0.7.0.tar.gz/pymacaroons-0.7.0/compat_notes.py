# attempt to match encryption scheme of libmacaroons.
# currently doesn't work

# this is the first part of add_third_party_caveat

old_key = self.signature
enc_key = self._truncate_or_pad(old_key)
print('enc_key')
print(enc_key)
print(len(enc_key))
enc_nonce = self._truncate_or_pad(b'\0', size=24)
print('enc_nonce')
print(enc_nonce)
print(len(enc_nonce))
derived_key = self._truncate_or_pad(self._generate_derived_key(key))
print('derived_key')
print(derived_key)
print(len(derived_key))
enc_plaintext = self._truncate_or_pad(b'\0', size=32) + self._truncate_or_pad(derived_key, size=32)
print('enc_plaintext')
print(enc_plaintext)
print(len(enc_plaintext))
box = SecretBox(key=enc_key)
nonced_ciphertext = box.encrypt(enc_plaintext, nonce=enc_nonce)
print('nonced_ciphertext')
print(nonced_ciphertext)
print(len(nonced_ciphertext))
unnonced_ciphertext = nonced_ciphertext[24:]
print('unnonced_ciphertext')
print(unnonced_ciphertext)
print(len(unnonced_ciphertext))
enc_ciphertext = self._truncate_or_pad(unnonced_ciphertext, size=64)
print('enc_ciphertext')
print(enc_ciphertext)
print(len(enc_ciphertext))
unpadded_vid = enc_ciphertext[16:64]
print('unpadded_vid')
print(unpadded_vid)
print(len(unpadded_vid))
verificationKeyId = base64.standard_b64encode(enc_nonce + unpadded_vid)
print('verificationKeyId')
print(verificationKeyId)
print(len(verificationKeyId))

whole_cipher = base64.standard_b64encode(nonced_ciphertext)
print('whole_cipher')
print(whole_cipher)
print(len(whole_cipher))
