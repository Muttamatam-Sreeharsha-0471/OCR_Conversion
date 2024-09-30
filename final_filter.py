import re
from rapidfuzz import process

'''PART 1: UNIT EXTRACTION AND NORMALIZATION'''

# Define a dictionary with full unit forms and their abbreviations
unit_fullform_to_abbreviation = {
    'centimetre': ['cm', 'centimeter', 'centimetres', 'centimeters'],
    'millimetre': ['mm', 'millimeter', 'millimetres', 'millimeters'],
    'metre': ['m', 'meter', 'meters', 'metres'],
    'inch': ['in', 'inches', '"'],
    'foot': ['ft', 'feet', "'"],
    'yard': ['yd', 'yards'],
    'gram': ['g', 'gm', 'gms', 'grams'],
    'kilogram': ['kg', 'kgs', 'kilograms'],
    'milligram': ['mg', 'mgs', 'milligrams'],
    'microgram': ['mcg', 'μg', 'micrograms'],
    'ounce': ['oz', 'ounces'],
    'pound': ['lb', 'lbs', 'pounds'],
    'ton': ['t', 'tonne', 'tonnes', 'tons'],
    'volt': ['v', 'volts'],
    'kilovolt': ['kv', 'kilovolts'],
    'millivolt': ['mv', 'millivolts'],
    'watt': ['w', 'watts'],
    'kilowatt': ['kw', 'kilowatts'],
    'litre': ['l', 'liters', 'litre', 'litres'],
    'millilitre': ['ml', 'milliliters', 'millilitres', 'mls'],
    'centilitre': ['cl', 'centiliters', 'centilitres'],
    'decilitre': ['dl', 'deciliters', 'decilitres'],
    'cubic foot': ['cu ft', 'ft³'],
    'cubic inch': ['cu in', 'in³'],
    'fluid ounce': ['fl oz', 'fluid ounces'],
    'gallon': ['gal', 'gallons'],
    'imperial gallon': ['imp gal', 'imperial gallons'],
    'pint': ['pt', 'pints'],
    'quart': ['qt', 'quarts'],
    'microlitre': ['ul', 'μl', 'microlitres', 'microliters'],
    'cup': ['cup', 'cups']
}

# Conversion factors to the smallest units (e.g., millimeters for length)
conversion_factors_to_smallest = {
    'millimetre': 1, 'centimetre': 10, 'metre': 1000, 'inch': 25.4, 'foot': 304.8, 'yard': 914.4,
    'milligram': 1, 'gram': 1000, 'kilogram': 1000000, 'microgram': 0.001, 'ounce': 28349.5, 'pound': 453592, 'ton': 1000000000,
    'millivolt': 1, 'volt': 1000, 'kilovolt': 1000000,
    'millilitre': 1, 'litre': 1000, 'centilitre': 10, 'decilitre': 100,
    'fluid ounce': 29.5735, 'gallon': 3785.41, 'pint': 473.176, 'quart': 946.353,
    'microlitre': 0.001, 'cubic inch': 16.3871, 'cubic foot': 28316.8,
    'watt': 1, 'kilowatt': 1000
}

# Unit categories for classification
unit_categories = {
    'length': {'millimetre', 'centimetre', 'metre', 'inch', 'foot', 'yard'},
    'weight': {'milligram', 'gram', 'kilogram', 'microgram', 'ounce', 'pound', 'ton'},
    'voltage': {'millivolt', 'volt', 'kilovolt'},
    'volume': {'millilitre', 'litre', 'centilitre', 'decilitre', 'fluid ounce', 'gallon', 'pint', 'quart', 'microlitre', 'cubic inch', 'cubic foot'},
    'wattage': {'watt', 'kilowatt'}
}

# Flatten the list of all unit abbreviations for fuzzy matching
all_units = [abbrev for unit_list in unit_fullform_to_abbreviation.values() for abbrev in unit_list]


def extract_numbers_with_units(text):
    """
    Extract numbers and corresponding units from text using regex and fuzzy matching.

    Parameters:
    text (str): The input text to extract numbers and units from.

    Returns:
    list: List of numbers with their normalized units.
    """
    pattern = r'(\d+(\.\d+)?)(\s*)([a-zA-Z]+)'  # Regex pattern to match numbers followed by unit strings
    matches = re.findall(pattern, text)

    results = []
    for match in matches:
        number = match[0]
        unit_candidate = match[3]
        # Fuzzy match the extracted unit with the closest valid unit abbreviation
        results_fuzzy = process.extractOne(unit_candidate, all_units, score_cutoff=95)
        if results_fuzzy:
            matched_unit = results_fuzzy[0]
            results.append(f"{number} {matched_unit}")  # Append the number and matched unit

    return results


'''PART 2: SEPARATION OF NUMBERS AND UNITS'''

def separate_numbers_and_units(output):
    """
    Separate numbers and units from the extracted results.

    Parameters:
    output (list): List of extracted number-unit pairs.

    Returns:
    tuple: Two lists containing numbers and corresponding units separately.
    """
    numbers_list = []
    units_list = []
    for item in output:
        match = re.match(r'([0-9.]+)\s*(\w+)', item)  # Regex to match number and unit
        if match:
            number, unit = match.groups()
            numbers_list.append(number)
            units_list.append(unit)

    return numbers_list, units_list


'''PART 3: CONVERT UNITS TO FULL FORMS'''

allowed_units = set(unit_fullform_to_abbreviation.keys())

def get_full_unit(unit_input):
    """
    Convert a unit abbreviation to its full form.

    Parameters:
    unit_input (str): Abbreviated unit string.

    Returns:
    str: Full form of the unit or an empty string if not found.
    """
    unit_input = re.sub(r'\s+', ' ', unit_input.lower().strip())  # Clean and normalize input

    for full_unit, abbreviations in unit_fullform_to_abbreviation.items():
        if unit_input == full_unit or unit_input in abbreviations:
            return full_unit

    return ""  # Return empty if no match is found


def convert_to_full_unit(input_text):
    """
    Extract numbers and units from text and convert units to their full forms.

    Parameters:
    input_text (str): Input text containing numbers and units.

    Returns:
    tuple: Final formatted result, list of numbers, list of full-form units.
    """
    output = extract_numbers_with_units(input_text)  # Extract numbers and fuzzy-matched units
    numbers, units = separate_numbers_and_units(output)

    # Convert units to full forms
    full_units = [get_full_unit(unit) for unit in units]
    final_result = [f"{num} {unit}" for num, unit in zip(numbers, full_units)]  # Combine numbers and full-form units

    return final_result, numbers, full_units


'''PART 4: CATEGORIZE AND CONVERT UNITS BASED ON CATEGORY'''

def categorize_values(numbers, result):
    """
    Categorize and convert the extracted values based on unit categories.

    Parameters:
    numbers (list): List of extracted numbers.
    result (list): List of corresponding full-form units.

    Returns:
    dict: Categorized values converted to their smallest units.
    """
    categorized_values = {
        'length': [], 'weight': [], 'voltage': [], 'volume': [], 'wattage': []
    }

    # Categorize and convert each value to its smallest unit
    for num, unit in zip(numbers, result):
        for category, unit_set in unit_categories.items():
            if unit in unit_set:
                converted_value = float(num) * conversion_factors_to_smallest[unit]
                categorized_values[category].append((converted_value, f"{num} {unit}"))

    return categorized_values


'''PART 5: GET ENTITY VALUE BASED ON CATEGORIZED UNITS'''

def get_entity_value(entity_value, categorized_values):
    """
    Get the appropriate value for the given entity based on the categorized units.

    Parameters:
    entity_value (str): The type of entity (e.g., 'item_weight', 'width', etc.).
    categorized_values (dict): The categorized values from the extracted units.

    Returns:
    str or None: The largest/smallest value for the entity or None if not found.
    """
    if entity_value in ['item_weight', 'maximum_weight_recommendation'] and categorized_values['weight']:
        return max(categorized_values['weight'], key=lambda x: x[0])[1]
    elif entity_value == 'voltage' and categorized_values['voltage']:
        return max(categorized_values['voltage'], key=lambda x: x[0])[1]
    elif entity_value == 'item_volume' and categorized_values['volume']:
        return max(categorized_values['volume'], key=lambda x: x[0])[1]
    elif entity_value == 'wattage' and categorized_values['wattage']:
        return max(categorized_values['wattage'], key=lambda x: x[0])[1]
    elif entity_value in ['width', 'depth', 'height'] and categorized_values['length']:
        if entity_value == 'width':
            return min(categorized_values['length'], key=lambda x: x[0])[1]  # Smallest width
        else:
            return max(categorized_values['length'], key=lambda x: x[0])[1]  # Largest depth/height

    return None  # Return None if no match found
