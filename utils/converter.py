from decimal import Decimal
from .constants import *


class Converter:

    def __call__(self, amount):
        self.amount = amount
        return self
        
    amount = 0
    to = ''
    from_unit = ''
    magnitude = 0

    conversions = {
        UNIT_MEASURE        : {'base': UNIT_MEASURE, 'conversion': 1},
        LITRE_MEASURE       : {'base': MILLILITRE_MEASURE, 'conversion': 1000},
        MILLILITRE_MEASURE  : {'base': MILLILITRE_MEASURE, 'conversion': 1},
        CUP_MEASURE         : {'base': MILLILITRE_MEASURE, 'conversion': 284.131},
        GALLON_MEASURE      : {'base': MILLILITRE_MEASURE, 'conversion': 4405},
        PINT_MEASURE        : {'base': MILLILITRE_MEASURE, 'conversion': 568.26125},
        QUART_MEASURE       : {'base': MILLILITRE_MEASURE, 'conversion': 1136.52},
        FLUID_OUNCE_MEASURE : {'base': MILLILITRE_MEASURE, 'conversion': 29.5735},
        KILOGRAM_MEASURE    : {'base': GRAM_MEASURE, 'conversion': 1000},
        GRAM_MEASURE        : {'base': GRAM_MEASURE, 'conversion': 1},
        MILLIGRAM_MEASURE   : {'base': GRAM_MEASURE, 'conversion': 0.001},
        POUND_MEASURE       : {'base': GRAM_MEASURE, 'conversion': 453.592},
        OUNCE_MEASURE       : {'base': GRAM_MEASURE, 'conversion': 28.3495},
    }

    def convert_to_base(self, unit, amount):
        return (Decimal(amount) * Decimal(self.conversions[unit]['conversion'])), self.conversions[unit]['base']

    def convert_from_base(self, unit, amount):
        return Decimal(amount) / Decimal(self.conversions[unit]['conversion'])

    def To(self, unit):
        self.to = unit
        if self.from_unit != '' and self.to != '' and self.conversions[self.from_unit]['base'] == self.conversions[self.to]['base']:
            base_amount, base_measure = self.convert_to_base(self.from_unit, self.amount)
            converted_amount = self.convert_from_base(self.to, base_amount)
            self.magnitude = round(converted_amount, 3)
            return self
        else:
            raise TypeError("Cannot convert {} to {}".format(self.from_unit, self.to))
            
    def From(self, unit):
        self.from_unit = unit
        return self