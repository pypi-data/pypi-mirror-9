# encoding: utf-8

from __future__ import absolute_import

import sys
import logging
import types

logger = logging.Logger('static_bundle')
stdouthandler = logging.StreamHandler(sys.stdout)
stdouthandler.setLevel(logging.DEBUG)
stdouthandler.setFormatter(logging.Formatter("\033[0;33m%(asctime)s - %(levelname)s - %(message)s\33[0m"))
logger.addHandler(stdouthandler)


def disable_logger_stdout():
    logger.removeHandler(stdouthandler)

TYPE_JS = 'js'
TYPE_CSS = 'css'
TYPE_OTHER = 'other'

ENV_PRODUCTION = 'production'
ENV_DEVELOPMENT = 'development'

BUNDLE_ITERABLE_TYPES = (list, tuple, types.GeneratorType)

from static_bundle.minifiers import DefaultMinifier
from static_bundle.configs import BuilderConfig

from static_bundle.bundles import (CssBundle,
                                   JsBundle,
                                   OtherFilesBundle,
                                   AbstractBundle)

from static_bundle.builders import (Asset,
                                    StandardBuilder)

from static_bundle.files import (JsFileResult,
                                 CssFileResult,
                                 StaticFileResult)

from static_bundle.handlers import (AbstractPrepareHandler,
                                    LessCompilerPrepareHandler)

from static_bundle.paths import (AbstractPath,
                                 FilePath,
                                 DirectoryPath)


