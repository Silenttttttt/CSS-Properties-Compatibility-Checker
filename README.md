# CSS Properties Compatibility Checker

This suite of scripts helps you download MDN browser compatibility data for CSS properties and then checks the compatibility of CSS properties used in provided .css or .vue files.

## Prerequisites:

1. Ensure you have Python installed.
2. Make sure `git` is installed and accessible from the command line.
3. Install required Python packages using:


```bash
pip install requests cssutils tqdm
```

## Instructions:

### 1. Downloading MDN Data:

Before you can evaluate the compatibility of your CSS properties, you first need to fetch the latest browser compatibility data from MDN.

Run the `Download_mdn_data.py` script:

```bash
python Download_mdn_data.py
```

This script will automatically clone the latest MDN browser compatibility data and save it as `consolidated_data.json`.

### 2. Evaluating CSS Compatibility:

Once you have the MDN data ready, you can now analyze your CSS properties.

Run the `Evaluate_css.py` script:

```bash
python Evaluate_css.py
```


You will be prompted to provide the path to a CSS or Vue.js file or directory. Enter the full path.

The script will then analyze the CSS properties in the provided files and compare them with the browser compatibility data from MDN.

Once completed, a `compatibility_results.json` file will be generated containing the compatibility results for the provided files.

## Workflow:

## Updating MDN Data:

To update the MDN data, simply run the `Download_mdn_data.py` script again. It will fetch the latest data and update the `consolidated_data.json`.

**Note**: This tool provides an approximation of browser compatibility based on MDN data. Always verify compatibility through extensive testing on actual browsers.

