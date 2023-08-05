import csv
import io
import os.path
from collections import namedtuple

def _normalize(entry):
    name = (entry.marketing_name or entry.model)
    brand = entry.retail_branding
    if not brand:
        return name

    norm_name = name.lower()
    norm_brand = brand.lower()
    if norm_name.startswith(norm_brand):
        return name

    return ' '.join((brand, name))

class Entry(object):
    def __init__(self, retail_branding, marketing_name, device, model):
        self.retail_branding = retail_branding
        self.marketing_name = marketing_name
        self.device = device
        self.model = model
        self.normalized_name = _normalize(self)

def iterate_entries():
    path = os.path.join(os.path.dirname(__file__), 'supported_devices.csv')
    with io.open(path, 'r') as fp:
        for i, fields in enumerate(csv.reader(fp)):
            if i == 0:
                # skip header field
                continue

            yield Entry(*[f.strip() for f in fields])
