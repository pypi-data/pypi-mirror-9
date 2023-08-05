#
#   Copyright (c) 2014-2015 eGauge Systems LLC
# 	4730 Walnut St, Suite 110
# 	Boulder, CO 80301
# 	voice: 720-545-9767
# 	email: davidm@egauge.net
#
#   All rights reserved.
#
#   This code is the property of eGauge Systems LLC and may not be
#   copied, modified, or disclosed without any prior and written
#   permission from eGauge Systems LLC.
#
default_app_config = 'epic.apps.EPIC_App_Config'

# Used in export.py to include the 'Bill To' address for orders.
BILL_TO_ADDRESS  = 'MyCompany Inc.\n' \
                   '1234 Street Blvd.\n' \
                   'Spaceport City, NM 87654'
SHIPPING_TYPE	 = 'FedEx Ground'	# default/preferred ship-type
SHIPPING_ACCOUNT = '123456789'

# When using the make-bom script to create a BOM (assembly) from a
# Kicad schematic, the part created to represent the BOM has the
# manufacturer name set to this string.
MANUFACTURER	= 'MyCompany'

# Directory containing KiCad-style footprints (.kicad_mod files):
KICAD_FOOTPRINTS_DIR	= '/usr/local/lib/kicad-lib/footprints/'
