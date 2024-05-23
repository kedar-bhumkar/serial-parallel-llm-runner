import json

# Function to convert JSON to the required format
def ros_pe_formatter(data):
    converted_data = {}
    #print(f"data - {data}")
    data = json.loads(data)
    for key, value in data.items():
        isDict = isinstance(value, dict)
        #print(f"value ={value} - isDict={isDict}")
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                new_key = f"{key} {sub_key}"
                converted_data[new_key] = sub_value
        else:
            converted_data[key] = value        
    return converted_data