#MAEC Bundle Reference Class

#Copyright (c) 2015, The MITRE Corporation
#All rights reserved

#Compatible with MAEC v4.1
#Last updated 08/14/2014

import maec
from . import _namespace
import maec.bindings.maec_bundle as bundle_binding
       
class BundleReference(maec.Entity):
    _namespace = _namespace
    _binding = bundle_binding
    _binding_class = bundle_binding.BundleReferenceType

    bundle_idref = maec.TypedField("bundle_idref")

    def __init__(self, bundle_idref = None):
        super(BundleReference, self).__init__()
        self.bundle_idref = bundle_idref
        