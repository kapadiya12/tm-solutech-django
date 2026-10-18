"""Country dialling data and validation, backed by Google's libphonenumber."""
from functools import lru_cache

import phonenumbers
from phonenumbers import PhoneNumberFormat

# Non-geographic / special regions we don't offer in the picker
_SKIP = {'001', 'AC', 'TA'}


@lru_cache(maxsize=1)
def countries():
    """[{iso, dial, lengths}] for every region with a calling code, sorted by ISO code.
    Country names are rendered client-side with Intl.DisplayNames (localised)."""
    rows = []
    for iso in sorted(phonenumbers.SUPPORTED_REGIONS - _SKIP):
        code = phonenumbers.country_code_for_region(iso)
        if not code:
            continue
        meta = phonenumbers.PhoneMetadata.metadata_for_region(iso)
        lengths = list(meta.general_desc.possible_length) if meta and meta.general_desc else []
        example = phonenumbers.example_number_for_type(iso, phonenumbers.PhoneNumberType.MOBILE) \
            or phonenumbers.example_number(iso)
        sample = phonenumbers.national_significant_number(example) if example else ''
        rows.append({'iso': iso, 'dial': code, 'lengths': [n for n in lengths if n > 0], 'example': sample})
    return rows


@lru_cache(maxsize=1)
def country_choices():
    return [(c['iso'], f"{c['iso']} +{c['dial']}") for c in countries()]


def normalise(national, iso):
    """Return (formatted_number, error). Empty input is allowed (phone is optional)."""
    national = (national or '').strip()
    if not national:
        return '', None
    if not all(ch.isdigit() or ch in ' -()+' for ch in national):
        return None, 'Use digits only. Spaces and dashes are fine.'
    try:
        number = phonenumbers.parse(national, iso)
    except phonenumbers.NumberParseException:
        return None, 'Please enter a valid phone number.'
    if not phonenumbers.is_possible_number(number):
        return None, 'This number has the wrong length for the selected country.'
    if not phonenumbers.is_valid_number(number):
        return None, 'Please check the number. It is not valid for the selected country.'
    formatted = phonenumbers.format_number(number, PhoneNumberFormat.INTERNATIONAL)
    if len(formatted) > 20:
        formatted = phonenumbers.format_number(number, PhoneNumberFormat.E164)
    return formatted, None
