# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
from xmldirector.plonecore.transformer_registry import TransformerRegistryUtility
from xmldirector.plonecore.validator_registry import ValidatorRegistryUtility

import xmldocument  # NOQA
import bibledocument  # NOQA

cwd = os.path.dirname(__file__)

TransformerRegistryUtility.register_transformation(
    'demo', 'shakespeare.xsl', os.path.join(cwd, 'shakespeare.xsl'))
TransformerRegistryUtility.register_transformation(
    'demo', 'sample-xslt2', os.path.join(cwd, 'sample_xslt2.xsl'), transformer_type='XSLT2')

TransformerRegistryUtility.register_transformation(
    'demo', 'sample-xslt3', os.path.join(cwd, 'sample_xslt3.xsl'), transformer_type='XSLT3')

ValidatorRegistryUtility.parse_folder('demo', cwd)

