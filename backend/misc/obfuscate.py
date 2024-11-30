import pickle
import base64
from backend.core.model.pydantic_models import *

# Define a sample class
class MyClass:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def __str__(self):
        return f"MyClass(name={self.name}, age={self.age})"

# Create an instance of the class
#obj = MyClass("Alice", 30)
obj = Cardiovascular(chest_pain="false", palpitations="false", dizziness="false", syncopal_episodes="false", new_swelling_in_legs="false", Cardiovascular_ROS__c="Assessed", Not_Assessed_Reason="Other", Reviewed_and_Negative="true", Lightheadedness="false", Use_of_Compression_Stockings="false", Systolic_Blood_Pressure="false", Diastolic_Blood_Pressure="false", Heart_Rate="false", Heart_Murmurs="false", Heart_Sounds="false", Edema="false", Pain_with_Walking="false", Chest_Pain="false", Palpitations="false", Dizziness="false" , Syncope="false" )


# Serialize and convert to Base64
def serialize_to_base64(obj):
    # Serialize the object using pickle
    serialized_data = pickle.dumps(obj)
    # Encode the serialized data into Base64
    base64_data = base64.b64encode(serialized_data)
    return base64_data.decode('utf-8')

# Deserialize from Base64
def deserialize_from_base64(base64_string):
    # Decode the Base64 string to bytes
    serialized_data = base64.b64decode(base64_string)
    # Deserialize the bytes back to the original object
    obj = pickle.loads(serialized_data)
    return obj

# Convert the object to Base64
base64_representation = serialize_to_base64(obj)
print("Base64 Representation:", base64_representation)
# Write the Base64 string to a file
with open('serialized_data.b64', 'w') as f:
    f.write(base64_representation)
print("Base64 data written to file")
base64_representation = None
# Read the Base64 string from the file
with open('serialized_data.b64', 'r') as f:
    base64_representation = f.read()

# Convert the Base64 string back to the object
restored_obj = deserialize_from_base64(base64_representation)
print("Restored Object:", restored_obj)
