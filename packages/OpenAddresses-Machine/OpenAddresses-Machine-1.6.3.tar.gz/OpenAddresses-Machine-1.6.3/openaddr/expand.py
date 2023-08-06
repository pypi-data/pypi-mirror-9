"""
Expand and alter case street names in US English

ie: "ST. SEBASTIAN ST" becomes "Saint Sebastian Street"

This code is a port of the Node conform's _expandElements function
  https://github.com/openaddresses/openaddresses-conform/blob/572b7a8066db107f028ecd5407fda0b2c7041d84/Tools/csv.js#L225
See also StreetNames, which is a similar but inverse function
  https://pypi.python.org/pypi/StreetNames
"""

# US English abbreviations. Origin:
# https://raw.githubusercontent.com/openaddresses/openaddresses-conform/572b7a8066db107f028ecd5407fda0b2c7041d84/Tools/expand.json
# A few of these have upper case keys; those are effectively disabled
abbreviation_table = {
    "aly": "alley",
    "arc": "arcade",
    "av": "avenue",
    "ave": "avenue",
    "blf": "bluff",
    "bl": "boulevard",
    "blvd": "boulevard",
    "br": "bridge",
    "brg": "bridge",
    "byp": "bypass",
    "ci": "circle",
    "cir": "circle",
    "cres": "crescent",
    "cr": "crescent",
    "crt": "court",
    "cswy": "causeway",
    "ct": "court",
    "ctr": "center",
    "cv": "cove",
    "dgnl": "diagonal",
    "dr": "drive",
    "expy": "expressway",
    "expwy": "expressway",
    "ewy": "freeway",
    "grd": "grade",
    "hbr": "harbor",
    "holw": "hollow",
    "hwy": "highway",
    "ln": "lane",
    "lp": "loop",
    "lndg": "landing",
    "mal": "mall",
    "mtwy": "motorway",
    "ovps": "overpass",
    "pk": "park",
    "pw": "parkway",
    "pky": "parkway",
    "pkwy": "parkway",
    "pl": "place",
    "plz": "plaza",
    "rd": "road",
    "rdg": "ridge",
    "rte": "route",
    "skwy": "sKyway",
    "sq": "square",
    "terr": "terrace",
    "tr": "terrace",
    "te": "terrace",
    "ter": "terrace",
    "tfwy": "trafficway",
    "thfr": "thoroughfare",
    "thwy": "thruway",
    "tpke": "turnpiKe",
    "trce": "trace",
    "tunl": "tunnel",
    "unp": "underpass",
    "wKwy": "walKway",
    "xing": "crossing",
    "anx": "annex",
    "arc": "arcade",
    "byu": "bayoo",
    "bch": "beach",
    "bnd": "bend",
    "btm": "bottom",
    "br": "branch",
    "brk": "brooK",
    "brks": "brooKs",
    "bg": "burg",
    "bgs": "burgs",
    "cp": "camp",
    "cyn": "canyon",
    "cpe": "cape",
    "ctrs": "centers",
    "cl": "close",
    "cirs": "circles",
    "clf": "cliff",
    "clfs": "cliffs",
    "clb": "club",
    "cmn": "common",
    "cor": "corner",
    "cors": "corners",
    "crse": "course",
    "cts": "courts",
    "cv": "cove",
    "cvs": "coves",
    "crK": "creeK",
    "crst": "crest",
    "xrd": "crossroad",
    "curv": "curve",
    "dl": "dale",
    "dm": "dam",
    "dv": "divide",
    "drs": "drives",
    "est": "estate",
    "ests": "estates",
    "ext": "extension",
    "exts": "extensions",
    "fls": "falls",
    "fry": "ferry",
    "fld": "field",
    "flds": "fields",
    "flt": "flat",
    "flts": "flats",
    "frd": "ford",
    "frds": "fords",
    "frst": "forest",
    "frg": "forge",
    "frgs": "forges",
    "frK": "forK",
    "frKs": "forKs",
    "ft": "fort",
    "gdn": "garden",
    "gdns": "gardens",
    "gtwy": "gateway",
    "gln": "glen",
    "glns": "glens",
    "grn": "green",
    "grns": "greens",
    "grv": "grove",
    "grvs": "groves",
    "hbrs": "harbours",
    "hvn": "haven",
    "hts": "heights",
    "hl": "hill",
    "hls": "hills",
    "inlt": "inlet",
    "is": "island",
    "iss": "islands",
    "jr": "junior",
    "jct": "junction",
    "jcts": "junctions",
    "Ky": "k",
    "Kys": "ks",
    "Knl": "Knoll",
    "Knls": "Knolls",
    "la": "lane",
    "lk": "lake",
    "lKs": "lakes",
    "lgt": "light",
    "lgts": "lights",
    "lf": "loaf",
    "lcK": "locK",
    "lcKs": "locKs",
    "ldg": "lodge",
    "mnr": "manor",
    "mnrs": "manors",
    "mdw": "meadow",
    "mdws": "meadows",
    "ml": "mill",
    "mls": "mills",
    "msn": "mission",
    "mt": "mount",
    "mtn": "mountain",
    "mtns": "mountains",
    "ncK": "necK",
    "orch": "orchard",
    "oval": "oval",
    "opas": "overpass",
    "psge": "passage",
    "pne": "pine",
    "pnes": "pines",
    "pln": "plain",
    "plns": "plains",
    "pt": "point",
    "pts": "points",
    "prt": "port",
    "prts": "ports",
    "pr": "prairie",
    "radl": "radial",
    "rnch": "ranch",
    "rpd": "rapid",
    "rpds": "rapids",
    "rst": "rest",
    "rdgs": "ridges",
    "riv": "river",
    "rds": "roads",
    "sr": "senior",
    "shl": "shoal",
    "shls": "shoals",
    "shr": "shore",
    "shrs": "shores",
    "spg": "spring",
    "spgs": "springs",
    "sqs": "squares",
    "sta": "station",
    "stra": "stravenue",
    "strm": "stream",
    "sts": "streets",
    "smt": "summit",
    "trwy": "throughway",
    "traK": "tracK",
    "trfy": "trafficway",
    "trl": "trail",
    "upas": "underpass",
    "un": "union",
    "uns": "unions",
    "vly": "valley",
    "vlys": "valleys",
    "via": "viaduct",
    "vw": "view",
    "vws": "views",
    "vlg": "village",
    "vlgs": "villages",
    "vl": "ville",
    "vis": "vista",
    "wl": "well",
    "wls": "wells",
    "wy": "way",
    "n": "north",
    "s": "south",
    "w": "west",
    "e": "east",
    "ne": "northeast",
    "nw": "northwest",
    "se": "southeast",
    "sw": "southwest",
    "rge": "range",
    "twp": "township"
}

def expand_street_name(street_name):
    "Perform expansion and conversion on street name"
    if street_name is None:
        return street_name

    # Strip whitespace, smash to lowercase, remove . from names
    street_name = street_name.strip().lower().replace(".", "")

    # Now substitute each word if it looks like an abbreviation
    tokenized = street_name.split(' ')
    for i, s in enumerate(tokenized):
        if s in abbreviation_table:
            tokenized[i] = abbreviation_table[s]
        # Special case Saint/Street depending on position
        if s == "st":
            if i >= len(tokenized)/2:
                tokenized[i] = "Street"
            else:
                tokenized[i] = "Saint"

    # Convert case to English
    case_converted = []
    for s in tokenized:
        if len(s) == 0:
            case_converted.append(s)
        elif s[0].isdigit():
            # special case: 3RD becomes 3rd, not 3Rd
            case_converted.append(s.lower())
        else:
            case_converted.append(s.title())

    street_name = ' '.join(case_converted)

    return street_name

import unittest
class TestExpand(unittest.TestCase):
    def test_expand_street_name(self):
        for e, a in (
            (None, None),
            ("", ""),
            ("Oak Drive", "OAK DR"),
            ("Oak Drive", "  OAK DR "),
            ("Oak Drive", "OAK DR."),
            ("Mornington Crescent", "MORNINGTON CR"),
        ):
            self.assertEqual(e, expand_street_name(a))

    def test_expand_street_name_st(self):
        for e, a in (
            ("Maple Street", "MAPLE ST"),
            ("Saint Isidore Drive", "ST ISIDORE DR"),
            ("Saint Sebastian Street", "ST. Sebastian ST"),
            ("Mornington Crescent", "MORNINGTON CR"),
        ):
            self.assertEqual(e, expand_street_name(a))

    def test_expand_case_exceptions(self):
        for e, a in (
            ("3rd Street", "3RD ST"),
        ):
            self.assertEqual(e, expand_street_name(a))
