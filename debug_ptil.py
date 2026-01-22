
from backend.ptil import PTILEncoder
from backend.token_mapper import TokenMapper

encoder = PTILEncoder()
mapper = TokenMapper()

prompt = "Please act as a relationship counselor. My partner and I are having trouble communicating. We argue about small things and it feels like we are drifting apart."

print(f"Original: '{prompt}'")
print(f"Original tokens: {mapper.count_tokens(prompt)}")

compressed = encoder.encode_and_serialize(prompt)

print(f"Compressed: '{compressed}'")
print(f"Compressed tokens: {mapper.count_tokens(compressed)}")
