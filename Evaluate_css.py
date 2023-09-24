import cssutils
import requests
import json
from tqdm import tqdm
import logging
import os

# Suppress cssutils logging to only critical issues
cssutils.log.setLevel(logging.CRITICAL)


def get_css_properties_from_file(css_content):
    """
    Extracts CSS properties from a given CSS content string.

    :param css_content: The CSS content string.
    :return: A set of CSS properties.
    """
    properties = set()
    parser = cssutils.CSSParser()
    stylesheet = parser.parseString(css_content)
    for rule in stylesheet:
        if isinstance(rule, cssutils.css.CSSStyleRule):
            for property in rule.style:
                properties.add(property.name)
    return properties


def get_css_properties_from_vue_file(file_path):
    """
    Extracts CSS properties from a Vue file.

    :param file_path: Path to the .vue file.
    :return: A set of CSS properties.
    """
    with open(file_path, 'r') as file:
        content = file.read()
        css_content = content.split('<style scoped>')[-1].split('</style>')[0].strip()
        return get_css_properties_from_file(css_content)


def load_mdn_data():
    """
    Load the MDN browser compatibility data from a local JSON file.

    :return: The loaded MDN data.
    """
    with open("consolidated_data.json", 'r') as file:
        return json.load(file)


def fetch_compatibility_data():
    """
    Fetches browser compatibility data from CanIUse.

    :return: The fetched compatibility data.
    """
    url = "https://raw.githubusercontent.com/Fyrd/caniuse/main/data.json"
    print("Fetching compatibility data...")
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching compatibility data: {e}")
        return {}
    return response.json()


def is_supported(browser_data):
    """
    Determines if a given CSS property is supported based on the browser data.

    :param browser_data: Data indicating browser support for a property.
    :return: True if supported, False otherwise.
    """
    if isinstance(browser_data, list):
        for entry in browser_data:
            if 'version_added' in entry and not entry.get('prefix'):
                return True
    elif isinstance(browser_data, dict):
        return 'version_added' in browser_data and not browser_data.get('prefix')
    return False


def calculate_compatibility_score(properties, compatibility_data, mdn_data):
    """
    Calculates compatibility scores based on the CSS properties and browser compatibility data.

    :param properties: CSS properties to check.
    :param compatibility_data: CanIUse compatibility data.
    :param mdn_data: MDN compatibility data.
    :return: Compatibility scores and least supported properties.
    """
    browsers = ['chrome', 'firefox', 'safari', 'edge', 'opera']
    scores = {browser: 0 for browser in browsers}
    property_scores = {}
    total_props = 0

    for prop in tqdm(properties, desc="Checking compatibility"):
        prop_score = 0
        if prop in mdn_data:
            support_data = mdn_data[prop]["support"]
            for browser in browsers:
                if is_supported(support_data.get(browser)):
                    scores[browser] += 1
                    prop_score += 1
            total_props += 1
        elif prop in compatibility_data["data"]:
            for browser in browsers:
                if is_supported(compatibility_data["data"][prop]["stats"][browser]):
                    scores[browser] += 1
                    prop_score += 1
            total_props += 1
        else:
            alt_name_found = False
            for mdn_prop, mdn_prop_data in mdn_data.items():
                alt_names = [entry.get("alternative_name") for support_data in mdn_prop_data["support"].values()
                             if isinstance(support_data, list) for entry in support_data if "alternative_name" in entry]
                if prop in alt_names:
                    for browser in browsers:
                        if is_supported(mdn_prop_data["support"].get(browser)):
                            scores[browser] += 1
                            prop_score += 1
                    alt_name_found = True
                    total_props += 1
                    break
            if not alt_name_found:
                print(f"Warning: No compatibility data found for the property '{prop}'.")

        property_scores[prop] = (prop_score / len(browsers)) * 100

    worst_offenders = [item for item in property_scores.items() if item[1] < 100]
    worst_offenders.sort(key=lambda x: x[1])

    for browser, score in scores.items():
        scores[browser] = round((score / total_props) * 100, 2)

    overall_score = round(sum(scores.values()) / len(browsers), 2)

    return scores, overall_score, worst_offenders[:10]


def get_key_from_path(path):
    """
    Extracts the last folder and filename from a path.

    :param path: The full file path.
    :return: The extracted key.
    """
    parts = path.split(os.sep)
    if len(parts) < 2:
        return path
    return os.path.join(parts[-2], parts[-1])


def process_file(file_path, mdn_data, compatibility_data):
    """
    Processes a given file (either .vue or .css) and returns compatibility scores.

    :param file_path: Path to the file.
    :param mdn_data: MDN compatibility data.
    :param compatibility_data: CanIUse compatibility data.
    :return: Compatibility scores and least supported properties.
    """
    if file_path.endswith('.vue'):
        properties = get_css_properties_from_vue_file(file_path)
    elif file_path.endswith('.css'):
        with open(file_path, 'r') as file:
            properties = get_css_properties_from_file(file.read())
    else:
        print("Unsupported file type!")
        return None, None

    if not properties:
        print("No CSS properties found!")
        return None, None

    return calculate_compatibility_score(properties, compatibility_data, mdn_data)


def main(input_path):
    """
    Main function that orchestrates the process.

    :param input_path: Path to the file or directory to process.
    """
    mdn_data = load_mdn_data()
    compatibility_data = fetch_compatibility_data()
    if not compatibility_data:
        print("Failed to fetch compatibility data.")
        return

    results = {}
    if os.path.isfile(input_path):
        file_scores, overall_score, least_supported = process_file(input_path, mdn_data, compatibility_data)
        if file_scores and overall_score:
            results[get_key_from_path(input_path)] = {
                'scores': file_scores,
                'overall_score': overall_score,
                'least_supported': least_supported
            }
    elif os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for file in tqdm(files, desc="Processing files"):
                file_path = os.path.join(root, file)
                file_scores, overall_score, least_supported = process_file(file_path, mdn_data, compatibility_data)
                if file_scores and overall_score:
                    results[get_key_from_path(file_path)] = {
                        'scores': file_scores,
                        'overall_score': overall_score,
                        'least_supported': least_supported
                    }

    with open("compatibility_results.json", 'w') as file:
        json.dump(results, file, indent=2)


if __name__ == "__main__":
    input_path = input("Please enter the path to your CSS or Vue.js directory/file: ")

    main(input_path)