import base64
import json

def base64url_decode(input):
    input += b'=' * (4 - (len(input) % 4))
    return base64.urlsafe_b64decode(input)

def base64url_encode(input):
    return base64.urlsafe_b64encode(input).replace(b'=', b'')

def to_json(a):   return json.dumps(a).encode('utf-8')
def from_json(a): return json.loads(a.decode('utf-8'))
def to_base64(a): return base64url_encode(a)
def from_base64(a): return base64url_decode(a)
def encode(a): return to_base64(to_json(a))
def decode(a): return from_json(from_base64(a))
