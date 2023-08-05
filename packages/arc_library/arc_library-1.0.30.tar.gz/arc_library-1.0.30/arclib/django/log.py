# -*- coding: utf-8 -*-
import sys

import logging
log = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setLevel(logging.DEBUG)
log.addHandler(handler)
log.setLevel(logging.DEBUG)

from arclib.django.object import ArcReturnJSONObject

