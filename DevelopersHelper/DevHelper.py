import json
import hashlib
import base64



def GenerateTEAL(filename : str):
    with open(filename) as f:
        data = json.load(f)

    stack_program_result = []

    stack_program_result.append("#pragma version 4\nint 0\n")
 
    for item in data['Interfaces']:
        for call_conf in item['methods']:
            name_method = call_conf['name'] 
            args_array = []
            for arg in call_conf['args']:
                args_array.append(arg['type'])
            #build the method signature in order to compute the hash
            method_signature = name_method + '('+','.join(args_array)+')'+call_conf['returns']['type']
            method_selector_hash = hashlib.sha256(method_signature.encode()).hexdigest()[0:8]
            #push the method selector into the stack 
            #print(method_selector_hash)
            stack_program_result.append(int(method_selector_hash, base=16)) #convert the hash to int before push into the stack

            for call_item in call_conf['call_config']:
                stack_program_result.append(call_item['ApplicationID'])
                stack_program_result.append(call_item['OnCompletion'])


    print(stack_program_result)
    return stack_program_result



GenerateTEAL("Test1.json")