UNIT_MEASURE = 'Unit'
LITRE_MEASURE = 'Litre'
MILLILITRE_MEASURE = 'Millilitre'
CUP_MEASURE = 'Cup'
GALLON_MEASURE = 'Gallon'
PINT_MEASURE = 'Pint'
QUART_MEASURE = 'Quart'
FLUID_OUNCE_MEASURE = 'Ounce(fl)'
KILOGRAM_MEASURE = 'Kilogram'
GRAM_MEASURE = 'Gram'
MILLIGRAM_MEASURE = 'Milligram'
POUND_MEASURE = 'Pound'
OUNCE_MEASURE = 'Ounce'
INVENTORY_PLAN = 'INVENTORY'
POS_PLAN = 'POS'
SALES_EMAIL = 'sales@vinocount.com'

KEG_WEIGHTS = {
    20: (6486.371, 26081.56),
    30: (7620.352, 37194.57),
    50: (13607.77, 63502.93),
    58: (14061.36, 72574.78),
    19000: (4626.642, 24584.71),
    20000: (6486.371, 26081.56),
    30000: (7620.352, 37194.57),
    50000: (13607.77, 63502.93),
    58600: (14061.36, 72574.78),
    58670: (14061.36, 72574.78),
}

SUPPLIER_ACTIVE_ORDER_STATES = [
    'pending_supplier_approval',
    'pending_client_approval',
    'pending_payment',
    'paid',
    'delivered_pending_payment'
]

CLIENT_ACTIVE_ORDER_STATES = [
    'draft',
    'pending_client_approval',
    'pending_payment',
    'paid',
    'delivered_pending_payment',
    'pending_supplier_approval'
]

class ACCOUNT_TYPES:
    STANDARD = 'standard'
    ORDERING = 'ordering'
    SUPPLIER = 'supplier'
    CHOICES = (
        ('client', 'client'),
        ('supplier', 'supplier')
    )

class SUPPLIER_TYPES:
    STANDARD = 'brewery'
    DISTILLERY = 'distillery'
    WINERY = 'winery'
    CHOICES = (
        ('brewery', 'brewery'),
        ('distillery', 'distillery'),
        ('winery', 'winery'),
    )