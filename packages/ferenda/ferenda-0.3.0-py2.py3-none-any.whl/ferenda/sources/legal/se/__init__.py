# flake8: noqa
from rdflib import Namespace
RPUBL = Namespace('http://rinfo.lagrummet.se/ns/2008/11/rinfo/publ#')
from .swedishlegalsource import SwedishLegalSource, SwedishLegalStore, SwedishCitationParser
from .regeringen import Regeringen
from .riksdagen import Riksdagen
from .trips import Trips, NoMoreLinks
from .arn import ARN
from .direktiv import Direktiv
from .ds import Ds
from .dv import DV
from .jk import JK
from .jo import JO
from .kommitte import Kommitte
from .myndfskr import MyndFskr
from .propositioner import Propositioner
from .sfs import SFS
from .sou import SOU

# these should be moved away from the "pure" swedish legal sources
# docrepos and into a lagen.nu specific package
from .lnkeyword import LNKeyword
from .lnwiki import LNMediaWiki
from .forarbeten import Forarbeten
