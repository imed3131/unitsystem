import yaml
import os 

def read_units_from_yaml(path: str):
    with open(path, "r") as file:
        data = yaml.safe_load(file)

    units = data.get("units", [])
    for unit in units:
        print(f"Name: {unit['name']}")
        print(f"Type: {unit['type']}")
        print(f"Base Unit: {unit['base']}")
        if unit["type"] == "linear":
            print(f"Factor to Base: {unit['factorToBase']}")
        elif unit["type"] == "functional":
            print(f"To Base: {unit['toBase']}")
            print(f"From Base: {unit['fromBase']}")
        print("-" * 30)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(script_dir, "units.yaml")
    print(f"Reading units from: {yaml_path}")
    read_units_from_yaml(yaml_path)
