import json
import hashlib

def GenerateTEAL(filename : str):
    with open(filename) as f:
        data = json.load(f)

    program = ""

    # generate TEAL code based on data
    # for example, using string concatenation:
    program += "int 0\n"

    for item in data:
        if item["type"] == "sha256":
            # compute SHA-256 hash of item["value"]
            hash = hashlib.sha256(item["value"].encode()).hexdigest()
            program += f"byte \"{hash}\"\n"
        elif item["type"] == "int":
            program += f"int {item['value']}\n"
        elif item["type"] == "str":
            program += f"byte \"{item['value']}\"\n"
        else:
            raise ValueError(f"Unknown type: {item['type']}")

    program += "pop\n"

    return program
