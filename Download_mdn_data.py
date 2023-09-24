import os
import json
import subprocess

def aggregate_data(directory_path):
    """
    Fetch data from all JSON files in the given directory.
    Returns a dictionary containing combined data.
    """
    aggregated_data = {}

    # Loop through every file in the directory
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        # Check if the current file is a JSON
        if filename.endswith(".json"):
            with open(file_path, 'r') as file:
                data = json.load(file)

                # Extract required data from the JSON content
                property_name = list(data["css"]["properties"].keys())[0]
                property_data = data["css"]["properties"][property_name]
                
                aggregated_data[property_name] = property_data

    return aggregated_data

def format_data(aggregated_data):
    """
    Reformat the aggregated data to include only necessary fields.
    """
    formatted_data = {}

    for property_name, property_data in aggregated_data.items():
        compat_data = property_data['__compat']

        formatted_entry = {
            'support': compat_data['support'],
            'status': compat_data['status']
        }

        # Add mdn_url and spec_url if they exist
        if 'mdn_url' in compat_data:
            formatted_entry['mdn_url'] = compat_data['mdn_url']
        if 'spec_url' in compat_data:
            formatted_entry['spec_url'] = compat_data['spec_url']

        formatted_data[property_name] = formatted_entry
    
    return formatted_data

def clone_mdn_repository():
    """
    Clone the MDN browser-compat-data repository's CSS properties folder.
    """
    repo_url = "https://github.com/mdn/browser-compat-data.git"
    subprocess.run(["git", "clone", "--depth=1", repo_url])
    os.rename("browser-compat-data/css/properties", "properties")
    subprocess.run(["rm", "-rf", "browser-compat-data"])

def main():
    clone_mdn_repository()
    
    directory_path = "properties"
    output_filename = "consolidated_data.json"

    aggregated_data = aggregate_data(directory_path)
    formatted_data = format_data(aggregated_data)

    # Save the formatted data to a single JSON file
    with open(output_filename, 'w') as outfile:
        json.dump(formatted_data, outfile, indent=4)

    # Clean up by deleting the properties folder
    subprocess.run(["rm", "-rf", "properties"])

    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    print("Starting the process to consolidate browser compatibility data...")
    main()
    print("Process completed!")
