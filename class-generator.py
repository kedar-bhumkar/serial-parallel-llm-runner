import json
from typing import Any, Dict

class ClassGenerator:
    def __init__(self, class_name: str, json_data: Dict[str, Any]):
        self.class_name = class_name
        self.json_data = json_data
    
    def generate_class_code(self) -> str:
        attributes = self._parse_json(self.json_data)
        class_code = f"class {self.class_name}:\n"
        class_code += "    def __init__(self, **kwargs):\n"
        for attr, attr_type in attributes.items():
            class_code += f"        self.{attr} = kwargs.get('{attr}', {self._get_default_value(attr_type)})\n"
        class_code += "\n"
        for attr, attr_type in attributes.items():
            class_code += f"    @property\n"
            class_code += f"    def {attr}(self) -> {attr_type}:\n"
            class_code += f"        return self.__dict__.get('{attr}', {self._get_default_value(attr_type)})\n\n"
            class_code += f"    @{attr}.setter\n"
            class_code += f"    def {attr}(self, value: {attr_type}):\n"
            class_code += f"        self.__dict__['{attr}'] = value\n\n"
        return class_code
    
    def _parse_json(self, json_data: Dict[str, Any]) -> Dict[str, str]:
        attributes = {}
        for key, value in json_data.items():
            attributes[key] = self._get_type(value)
        return attributes
    
    def _get_type(self, value: Any) -> str:
        if isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, bool):
            return "bool"
        elif isinstance(value, dict):
            return "dict"
        elif isinstance(value, list):
            return "list"
        else:
            return "str"
    
    def _get_default_value(self, attr_type: str) -> str:
        if attr_type == "int":
            return "0"
        elif attr_type == "float":
            return "0.0"
        elif attr_type == "bool":
            return "False"
        elif attr_type == "dict":
            return "{}"
        elif attr_type == "list":
            return "[]"
        else:
            return "''"

# Example usage
json_input = '''
{"visittype":"follow-up","dateofvisit":"","memberneworestablished":"new","placeofservice":"home","hastherebeenafall?":"no","historyofpresentillness":"hypertension,cabg2yearsago,acutebronchitis"}
'''
data = json.loads(json_input)
generator = ClassGenerator("Person", data)
class_code = generator.generate_class_code()
print(class_code)
