#!/usr/bin/env python
#-*- coding : utf-8 -*-

from ..rest import *

cli = BaeRest("http://newcode.bce.duapp.com:8080", debug = True)
res = cli.get("/apps/testapp")
print res
