import boto
import base64


kms = boto.connect_kms()

key_id = "bcc067ff-2868-47fb-98f2-a6e158b4fc9f"

data = 'My text'

#data = data.encode('utf-8')

data = b'\x00\x01\x02\x03\x04\x05'

#data = base64.b64encode(data)
response = kms.encrypt(key_id=key_id, plaintext=data)

encrypted = response['CiphertextBlob']


response = kms.decrypt(ciphertext_blob=encrypted)

original = response['Plaintext']
print(original)
#unencoded_original = base64.b64decode(original.encode('utf-8'))
#print(unencoded_original)
#print(unencoded_original.decode('utf-8'))
