import base64
import inspect
from typing import Type, Union, Any
from pathlib import Path
from typing import Annotated, List, Literal, Optional
from pydantic import BaseModel, Field, Strict,Base64Bytes

def encode_class_to_file(
    cls: Type[Any], 
    output_path: Union[str, Path]
) -> bool:
    """
    Encodes a Python class and saves it to a file.
    
    Args:
        cls: The class to encode
        output_path: Path where the encoded class will be saved
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get the source code of the class
        class_code = inspect.getsource(cls)
        
        # Encode the class code to base64
        encoded_bytes = base64.b64encode(class_code.encode('utf-8'))
        encoded_string = encoded_bytes.decode('utf-8')
        
        # Convert path to Path object if string
        output_path = Path(output_path)
        
        # Write encoded string to file
        output_path.write_text(encoded_string)
        return True
        
    except (TypeError, OSError, AttributeError) as e:
        print(f"Error encoding class: {str(e)}")
        return False

def decode_class_from_file(
    file_path: Union[str, Path]
) -> Union[str, None]:
    """
    Decodes a class specification from an encoded file.
    
    Args:
        file_path: Path to the encoded class file
        
    Returns:
        str: Decoded class code if successful, None otherwise
    """
    try:
        # Convert path to Path object if string
        file_path = Path(file_path)
        
        # Read encoded content
        encoded_content = file_path.read_text()
        
        # Decode from base64
        decoded_bytes = base64.b64decode(encoded_content)
        decoded_string = decoded_bytes.decode('utf-8')
        
        return decoded_string
        
    except (OSError, base64.binascii.Error) as e:
        print(f"Error decoding class: {str(e)}")
        return None

# Example usage:
if __name__ == "__main__":
 
    class ExampleClass:
        def __init__(self, name: str):
            self.name = name
            
        def greet(self) -> str:
            return f"Hello, {self.name}!"
    # Encode and save
    success = encode_class_to_file(ExampleClass, "encoded_class.txt")
    if success:
        print("Class encoded successfully")
    
    # Decode and print
    decoded_code = decode_class_from_file("encoded_class.txt")
    if decoded_code:
        print("\nDecoded class code:")
        print(decoded_code)
