from strings import STRINGS
import json

uz = STRINGS['uz']
ru = STRINGS['ru']

all_keys = set(uz.keys()) | set(ru.keys())
missing = []

for k in all_keys:
    if k not in uz:
        missing.append(f"Key '{k}' missing in UZ")
    if k not in ru:
        missing.append(f"Key '{k}' missing in RU")

for m in sorted(missing):
    print(m)
