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
from datetime import datetime, timedelta
from epic import KICAD_FOOTPRINTS_DIR as DIR

import os
import re

class Footprints:
    last_update = datetime.now()
    list = None

    @classmethod
    def get(cls):
        if Footprints.list is None \
           or(datetime.now() - Footprints.last_update
              > timedelta(seconds=600)):
            Footprints.list = []
            pattern = re.compile(r'([.]pretty(/|$))')
            for root, dirs, files in os.walk(DIR):
                libname = pattern.sub(':', root[len(DIR):])
                for f in files:
                    m = re.match(r'(.*)[.]kicad_mod$', f)
                    if m:
                        Footprints.list.append(libname + m.group(1))
            Footprints.last_update = datetime.now()
        return Footprints.list
