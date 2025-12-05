#!/usr/bin/env python3
"""
make_cfb2026_full_metadata.py

Generates: CFB_2026_full_metadata.json

Contents:
 - All FBS + FCS conferences (projected 2026 membership)
 - For each team: name, colors (list of color names), offense_scheme, defense_scheme,
   rivalries (list), prestige (0-100 heuristic), notes (string)

Notes:
 - This script uses a mix of authoritative-known values (for many major programs)
   and systematic heuristics/inference for the remaining teams.
 - Please review teams you care about and adjust values (colors/schemes/rivalries/prestige)
   where you need exact accuracy.
"""

import json
import os
from collections import defaultdict

# ---------------------------
# 1) Projected 2026 team lists (FBS + FCS)
# These are taken from the previous dataset built in conversation.
# ---------------------------
CFB_2026 = {
    "FBS": {
        "conferences": {
            "SEC": {"teams": ["Alabama Crimson Tide","Arkansas Razorbacks","Auburn Tigers","Florida Gators","Georgia Bulldogs","Kentucky Wildcats","LSU Tigers","Mississippi State Bulldogs","Missouri Tigers","Ole Miss Rebels","South Carolina Gamecocks","Tennessee Volunteers","Texas A&M Aggies","Vanderbilt Commodores"]},
            "Big Ten": {"teams": ["Illinois Fighting Illini","Indiana Hoosiers","Iowa Hawkeyes","Maryland Terrapins","Michigan Wolverines","Michigan State Spartans","Minnesota Golden Gophers","Nebraska Cornhuskers","Northwestern Wildcats","Ohio State Buckeyes","Penn State Nittany Lions","Purdue Boilermakers","Rutgers Scarlet Knights","Wisconsin Badgers","USC Trojans","UCLA Bruins","Oregon Ducks","Washington Huskies"]},
            "ACC": {"teams": ["Boston College Eagles","Clemson Tigers","Duke Blue Devils","Florida State Seminoles","Georgia Tech Yellow Jackets","Louisville Cardinals","Miami Hurricanes","NC State Wolfpack","North Carolina Tar Heels","Pittsburgh Panthers","SMU Mustangs","Stanford Cardinal","Syracuse Orange","Virginia Cavaliers","Virginia Tech Hokies","Wake Forest Demon Deacons"]},
            "Big 12": {"teams": ["Baylor Bears","BYU Cougars","Central Florida Knights","Cincinnati Bearcats","Houston Cougars","Kansas Jayhawks","Kansas State Wildcats","Oklahoma State Cowboys","TCU Horned Frogs","Texas Longhorns","Iowa State Cyclones","West Virginia Mountaineers","Arizona State Sun Devils","Arizona Wildcats","Colorado Buffaloes","Utah Utes"]},
            "Pac-12": {"teams": ["Boise State Broncos","Colorado State Rams","Fresno State Bulldogs","San Diego State Aztecs","Utah State Aggies","Texas State Bobcats","Oregon State Beavers","Washington State Cougars"]},
            "Mountain West Conference":{"teams":["Air Force Falcons","Boise State Broncos","Colorado State Rams","Fresno State Bulldogs","Hawai'i Rainbow Warriors","Nevada Wolf Pack","New Mexico Lobos","San Diego State Aztecs","San Jose State Spartans","UNLV Rebels","Utah State Aggies","Wyoming Cowboys"]},
            "Sun Belt Conference":{"teams":["Appalachian State Mountaineers","Arkansas State Red Wolves","Coastal Carolina Chanticleers","Georgia Southern Eagles","Georgia State Panthers","James Madison Dukes","Louisiana Ragin' Cajuns","Marshall Thundering Herd","Old Dominion Monarchs","South Alabama Jaguars","Southern Miss Golden Eagles","Troy Trojans"]},
            "Conference USA":{"teams":["Charlotte 49ers","Florida Atlantic Owls","FIU Panthers","Louisiana Tech Bulldogs","Middle Tennessee Blue Raiders","North Texas Mean Green","Rice Owls","UTEP Miners","UTSA Roadrunners","Western Kentucky Hilltoppers"]},
            "Mid-American Conference":{"teams":["Akron Zips","Ball State Cardinals","Bowling Green Falcons","Buffalo Bulls","Central Michigan Chippewas","Eastern Michigan Eagles","Kent State Golden Flashes","Miami (OH) RedHawks","Northern Illinois Huskies","Ohio Bobcats","Toledo Rockets","Western Michigan Broncos"]},
            "American Athletic Conference":{"teams":["Cincinnati Bearcats","East Carolina Pirates","Houston Cougars","Memphis Tigers","Navy Midshipmen","SMU Mustangs","Temple Owls","Tulane Green Wave","Tulsa Golden Hurricane","UCF Knights"]},
            "FBS Independents":{"teams":["Army Black Knights","Notre Dame Fighting Irish","UMass Minutemen","UConn Huskies"]}
        }
    },
    "FCS": {
        "conferences": {
            "Big Sky Conference":{"teams":["Cal Poly Mustangs","Eastern Washington Eagles","Idaho Vandals","Idaho State Bengals","Montana Grizzlies","Montana State Bobcats","Northern Arizona Lumberjacks","Northern Colorado Bears","Portland State Vikings","Sacramento State Hornets","UC Davis Aggies","Weber State Wildcats"]},
            "Missouri Valley Football Conference":{"teams":["Illinois State Redbirds","Indiana State Sycamores","Missouri State Bears","North Dakota State Bison","Northern Iowa Panthers","South Dakota Coyotes","South Dakota State Jackrabbits","Southern Illinois Salukis","Western Illinois Leathernecks","Youngstown State Penguins"]},
            "Southern Conference":{"teams":["Chattanooga Mocs","East Tennessee State Buccaneers","Furman Paladins","The Citadel Bulldogs","Mercer Bears","Samford Bulldogs","VMI Keydets","Western Carolina Catamounts"]},
            "Southland Conference":{"teams":["Houston Christian Huskies","Incarnate Word Cardinals","McNeese Cowboys","Northwestern State Demons","Nicholls Colonels","Southeastern Louisiana Lions","Texas A&M–Commerce Lions","Stephen F. Austin Lumberjacks"]},
            "Southwestern Athletic Conference":{"teams":["Alabama A&M Bulldogs","Alabama State Hornets","Alcorn State Braves","Jackson State Tigers","Mississippi Valley State Delta Devils","Prairie View A&M Panthers","Southern Jaguars","Texas Southern Tigers"]},
            "United Athletic Conference":{"teams":["Austin Peay Governors","Eastern Kentucky Colonels","Jacksonville State Gamecocks","Kennesaw State Owls","Lamar Cardinals","Sam Houston Bearkats","Stephen F. Austin Lumberjacks","Southern Utah Thunderbirds","UTRGV Vaqueros","Weber State Wildcats"]},
            "Ivy League":{"teams":["Brown Bears","Columbia Lions","Cornell Big Red","Dartmouth Big Green","Harvard Crimson","Penn Quakers","Princeton Tigers","Yale Bulldogs"]},
            "CAA Football":{"teams":["Albany Great Danes","Delaware Fightin' Blue Hens","Elon Phoenix","Hampton Pirates","Maine Black Bears","Monmouth Hawks","New Hampshire Wildcats","Rhode Island Rams","Stony Brook Seawolves","Towson Tigers","Richmond Spiders"]},
            "FCS Independents":{"teams":["Merrimack Warriors","Sacred Heart Pioneers"]}
        }
    }
}

# ---------------------------
# 2) Known metadata for many major programs (colors, schemes, rivalries, prestige)
#    This list is intentionally longer for major programs; rest will be heuristically inferred.
# ---------------------------
KNOWN_METADATA = {
    # SEC
    "Alabama Crimson Tide": {"colors":["Crimson","White"], "offense_scheme":"Pro-Style/Multiple", "defense_scheme":"4-2-5", "rivalries":["Auburn (Iron Bowl)","Tennessee"], "prestige":96, "notes":"Dynasty program; many natl titles."},
    "Georgia Bulldogs": {"colors":["Red","Black"], "offense_scheme":"Inside Zone/Pro-Style", "defense_scheme":"3-4", "rivalries":["Georgia Tech","Florida"], "prestige":95, "notes":"Recent national success."},
    "LSU Tigers": {"colors":["Purple","Gold"], "offense_scheme":"Spread/Pro-Style hybrid", "defense_scheme":"3-4", "rivalries":["Ole Miss","Alabama"], "prestige":87, "notes":""},
    "Texas A&M Aggies": {"colors":["Maroon","White"], "offense_scheme":"Pro-Style/Spread", "defense_scheme":"4-2-5", "rivalries":["Texas (Rivalry)"], "prestige":80, "notes":""},
    "Florida Gators": {"colors":["Orange","Blue"], "offense_scheme":"Spread/Pro-Style", "defense_scheme":"4-3", "rivalries":["Georgia","Florida State"], "prestige":85, "notes":""},
    "Tennessee Volunteers": {"colors":["Orange","White"], "offense_scheme":"Spread/Multiple", "defense_scheme":"4-2-5", "rivalries":["Alabama","Vanderbilt"], "prestige":82, "notes":""},
    "Auburn Tigers": {"colors":["Navy","Burnt Orange"], "offense_scheme":"Pro-Style/Spread", "defense_scheme":"4-3", "rivalries":["Alabama (Iron Bowl)"], "prestige":81, "notes":""},
    "Ole Miss Rebels": {"colors":["Cardinal","Navy"], "offense_scheme":"Spread/Pass-Heavy", "defense_scheme":"4-3", "rivalries":["Mississippi State (Egg Bowl)"], "prestige":70, "notes":""},
    "Arkansas Razorbacks": {"colors":["Cardinal","White"], "offense_scheme":"Multiple/Spread", "defense_scheme":"4-2-5", "rivalries":["LSU","Ole Miss"], "prestige":65, "notes":""},
    "Missouri Tigers": {"colors":["Black","Gold"], "offense_scheme":"Spread/Pro-Style", "defense_scheme":"4-3", "rivalries":["Kansas (Little Rock rivalry historically)"], "prestige":64, "notes":""},
    "Mississippi State Bulldogs": {"colors":["Maroon","White"], "offense_scheme":"Multiple", "defense_scheme":"4-3", "rivalries":["Ole Miss (Egg Bowl)"], "prestige":60, "notes":""},
    "South Carolina Gamecocks": {"colors":["Garnet","Black"], "offense_scheme":"Pro-Style/Multiple", "defense_scheme":"4-3", "rivalries":["Clemson"], "prestige":62, "notes":""},
    "Kentucky Wildcats": {"colors":["Blue","White"], "offense_scheme":"Spread/Multiple", "defense_scheme":"4-3", "rivalries":["Louisville"], "prestige":55, "notes":""},
    "Vanderbilt Commodores": {"colors":["Black","Gold"], "offense_scheme":"Pro-Style", "defense_scheme":"4-3", "rivalries":["Tennessee"], "prestige":42, "notes":""},

    # Big Ten / West coast additions
    "Ohio State Buckeyes": {"colors":["Scarlet","Gray"], "offense_scheme":"Balanced/Spread", "defense_scheme":"4-3", "rivalries":["Michigan (The Game)","Penn State"], "prestige":94, "notes":""},
    "Michigan Wolverines": {"colors":["Maize","Blue"], "offense_scheme":"Pro-Style/Spread", "defense_scheme":"4-3", "rivalries":["Ohio State"], "prestige":92, "notes":""},
    "Penn State Nittany Lions": {"colors":["Blue","White"], "offense_scheme":"Pro-Style/Multiple", "defense_scheme":"4-3", "rivalries":["Ohio State","Michigan"], "prestige":88, "notes":""},
    "USC Trojans": {"colors":["Cardinal","Gold"], "offense_scheme":"Pro-Style/Spread", "defense_scheme":"4-3", "rivalries":["UCLA","Notre Dame"], "prestige":88, "notes":""},
    "Oregon Ducks": {"colors":["Green","Yellow"], "offense_scheme":"Spread/Tempo", "defense_scheme":"3-4", "rivalries":["Oregon State"], "prestige":82, "notes":""},
    "Washington Huskies": {"colors":["Purple","Gold"], "offense_scheme":"Pro-Style/Spread", "defense_scheme":"4-3", "rivalries":["Washington State (Apple Cup)"], "prestige":80, "notes":""},
    "UCLA Bruins": {"colors":["Blue","Gold"], "offense_scheme":"Spread/Pro-Style", "defense_scheme":"3-4", "rivalries":["USC"], "prestige":75, "notes":""},

    # ACC / prominent
    "Clemson Tigers": {"colors":["Orange","Regalia"], "offense_scheme":"Pro-Style/Spread", "defense_scheme":"4-3/3-4 hybrid", "rivalries":["South Carolina"], "prestige":90, "notes":""},
    "Florida State Seminoles": {"colors":["Garnet","Gold"], "offense_scheme":"Pro-Style/Spread", "defense_scheme":"4-3", "rivalries":["Miami","Florida"], "prestige":86, "notes":""},
    "Miami Hurricanes": {"colors":["Orange","Green"], "offense_scheme":"Pro-Style/Spread", "defense_scheme":"4-3", "rivalries":["Florida State","FLORIDA"], "prestige":84, "notes":""},

    # Big 12 / notable
    "Texas Longhorns": {"colors":["Burnt Orange","White"], "offense_scheme":"Spread/Pro-Style mix", "defense_scheme":"4-3", "rivalries":["Oklahoma (Red River)","Texas A&M"], "prestige":89, "notes":""},
    "Oklahoma State Cowboys": {"colors":["Orange","Black"], "offense_scheme":"Spread/Run-heavy", "defense_scheme":"3-3-5", "rivalries":["Oklahoma (Bedlam)"], "prestige":78, "notes":""},
    "Kansas State Wildcats": {"colors":["Royal Purple","White"], "offense_scheme":"Spread/Multiple", "defense_scheme":"4-2-5", "rivalries":["Kansas"], "prestige":63, "notes":""},
    "TCU Horned Frogs": {"colors":["Purple","White"], "offense_scheme":"Spread/Run-Pass", "defense_scheme":"4-2-5", "rivalries":["Baylor"], "prestige":74, "notes":""},

    # Notable Group of Five / Independents
    "Notre Dame Fighting Irish": {"colors":["Blue","Gold"], "offense_scheme":"Multiple/Pro-Style", "defense_scheme":"4-3", "rivalries":["USC","Navy"], "prestige":90, "notes":"Independent powerhouse historically"},
    "BYU Cougars": {"colors":["Navy","White"], "offense_scheme":"Spread/Multiple", "defense_scheme":"3-4", "rivalries":["Utah (Holy War)"], "prestige":68, "notes":""},
    "UCF Knights": {"colors":["Black","Gold"], "offense_scheme":"Spread/Up-tempo", "defense_scheme":"4-2-5", "rivalries":["South Florida"], "prestige":60, "notes":""},

    # Service academies
    "Army Black Knights": {"colors":["Black","Gold"], "offense_scheme":"Triple Option", "defense_scheme":"3-4", "rivalries":["Navy"], "prestige":65, "notes":""},
    "Navy Midshipmen": {"colors":["Navy Blue","Gold"], "offense_scheme":"Triple Option", "defense_scheme":"4-3", "rivalries":["Army"], "prestige":64, "notes":""},

    # FCS notable
    "North Dakota State Bison": {"colors":["Yellow","Green"], "offense_scheme":"Power/Zone-Run", "defense_scheme":"4-2-5", "rivalries":["South Dakota State"], "prestige":85, "notes":"FCS dynasty"},
    "Montana Grizzlies": {"colors":["Copper","Silver"], "offense_scheme":"Pro-Style/Multiple", "defense_scheme":"4-3", "rivalries":["Montana State (Brawl of the Wild)"], "prestige":72, "notes":""},

    # example others (many more will be created by heuristics)
    "Appalachian State Mountaineers": {"colors":["Black","Gold"], "offense_scheme":"Spread/Option", "defense_scheme":"3-4", "rivalries":["Marshall","Georgia Southern"], "prestige":70, "notes":""},
    "James Madison Dukes": {"colors":["Purple","Gold"], "offense_scheme":"Spread/Pro-Style mix", "defense_scheme":"4-3", "rivalries":["Old Dominion"], "prestige":68, "notes":""},
    "Marshall Thundering Herd": {"colors":["Green","White"], "offense_scheme":"Spread/Pro-Style", "defense_scheme":"4-3", "rivalries":["Ohio", "App State"], "prestige":66, "notes":""},
    # ... additional known entries could be extended here ...
}

# ---------------------------
# 3) Heuristics / helpers to infer metadata for teams not explicitly listed
# ---------------------------

# Basic color hints by keyword in school name (very rough)
GENERIC_COLOR_MAP = {
    "Alabama": ["Crimson","White"],
    "A&M": ["Maroon","White"],
    "State": ["Blue","White"],
    "Tech": ["Black","Gold"],
    "University": ["Blue","White"],
    "Saint": ["Navy","White"],
    "Navy": ["Navy Blue","Gold"],
    "Air Force": ["Blue","Silver"],
    "Army": ["Black","Gold"],
    "Troy": ["Cardinal","Silver"],
    "Georgia": ["Red","Black"],
    "Central": ["Blue","White"],
    "Northern": ["Navy","White"],
    "Southern": ["Blue","Gold"],
    "Western": ["Brown","Gold"]
}

# Default scheme by conference (inferred defaults)
CONFERENCE_DEFAULT_SCHEMES = {
    "SEC": {"offense":"Pro-Style/Spread","defense":"4-3/4-2-5"},
    "Big Ten": {"offense":"Pro-Style/Spread","defense":"4-3"},
    "ACC": {"offense":"Pro-Style/Spread","defense":"4-3"},
    "Big 12": {"offense":"Spread/Tempo","defense":"3-3-5"},
    "Pac-12": {"offense":"Spread/Tempo","defense":"3-4"},
    "Mountain West Conference": {"offense":"Spread/Pro-Style","defense":"4-3"},
    "Sun Belt Conference": {"offense":"Spread","defense":"4-2-5"},
    "Conference USA": {"offense":"Spread","defense":"4-3"},
    "Mid-American Conference": {"offense":"Balanced/Spread","defense":"4-3"},
    "American Athletic Conference": {"offense":"Spread","defense":"4-3"},
    "FBS Independents": {"offense":"Multiple","defense":"4-3"},
    # FCS conferences - defaults
    "Big Sky Conference": {"offense":"Spread","defense":"3-4"},
    "Missouri Valley Football Conference": {"offense":"Pro-Style/Spread","defense":"4-2-5"},
    "Southern Conference": {"offense":"Pro-Style","defense":"4-3"},
    "Southland Conference": {"offense":"Spread","defense":"4-3"},
    "Southwestern Athletic Conference": {"offense":"Pro-Style","defense":"4-3"},
    "United Athletic Conference": {"offense":"Spread","defense":"4-3"},
    "Ivy League": {"offense":"Pro-Style","defense":"4-3"},
    "CAA Football": {"offense":"Pro-Style/Spread","defense":"4-3"},
    "FCS Independents": {"offense":"Unknown","defense":"Unknown"}
}

# Simple prestige base by conference tier
CONFERENCE_PRESTIGE_BASE = {
    "SEC": 85,
    "Big Ten": 84,
    "ACC": 78,
    "Big 12": 76,
    "Pac-12": 76,
    "Mountain West Conference": 64,
    "Sun Belt Conference": 58,
    "Conference USA": 55,
    "Mid-American Conference": 52,
    "American Athletic Conference": 60,
    "FBS Independents": 65,
    # FCS
    "Big Sky Conference": 50,
    "Missouri Valley Football Conference": 62,
    "Southern Conference": 50,
    "Southland Conference": 40,
    "Southwestern Athletic Conference": 45,
    "United Athletic Conference": 48,
    "Ivy League": 58,
    "CAA Football": 56,
    "FCS Independents": 35
}

def infer_colors(team_name):
    # Try to find a generic color mapping based on keywords
    for key, colors in GENERIC_COLOR_MAP.items():
        if key.lower() in team_name.lower():
            return colors
    # Fallback: try to parse common words
    if "Trojans" in team_name or "USC" in team_name:
        return ["Cardinal","Gold"]
    if "Ducks" in team_name or "Oregon" in team_name:
        return ["Green","Yellow"]
    return ["Unknown"]

def infer_schemes(team_name, conference):
    conf_defaults = CONFERENCE_DEFAULT_SCHEMES.get(conference, {"offense":"Unknown","defense":"Unknown"})
    return conf_defaults["offense"], conf_defaults["defense"]

def infer_prestige(team_name, conference):
    base = CONFERENCE_PRESTIGE_BASE.get(conference, 50)
    # slight modifications based on name cues (Power programs)
    name_lower = team_name.lower()
    if any(x in name_lower for x in ["alabama","ohio state","georgia","usc","michigan","notre dame","texas","oklahoma","clemson","lsu","oklahoma"]):
        # already captured in KNOWN_METADATA but extra guard
        return min(99, base + 12)
    # small adjustment by program length (heuristic)
    if "state" in name_lower or "tech" in name_lower or "a&m" in name_lower:
        adj = -3
    else:
        adj = 0
    return max(10, min(95, base + adj))

def pick_rivalries(team_name, conference, teams_in_conf):
    # If known historical rivals exist in KNOWN_METADATA, keep them.
    # Otherwise infer a rivalry: prefer same-state opponents, then long-standing conference foes.
    rivals = []
    tn = team_name.lower()
    # same-state search
    words = [w for w in tn.replace("'", "").replace("–"," ").split() if len(w)>2]
    for other in teams_in_conf:
        if other == team_name:
            continue
        ol = other.lower()
        # same state (very rough): check full state names (major schools) or shared city word
        for w in ["state","texas","north","south","west","east","montana","cal","california","kansas","oklahoma","alabama","georgia","florida","tennessee","missouri","louisiana","arkansas","virginia","kentucky"]:
            if w in tn and w in ol and other not in rivals:
                rivals.append(other)
    # if none, add top conference rival by proximity in list
    if not rivals and teams_in_conf:
        # pick a close index neighbor as a plausible rival
        try:
            idx = teams_in_conf.index(team_name)
            # neighbor left or right
            if idx>0:
                rivals.append(teams_in_conf[idx-1])
            if idx < len(teams_in_conf)-1:
                rivals.append(teams_in_conf[idx+1])
        except ValueError:
            pass
    # limit to 3
    return rivals[:3]

# ---------------------------
# 4) Build final metadata dataset
# ---------------------------

def build_full_metadata(cfb_structure, known_meta):
    out = {"FBS":{"conferences":{}}, "FCS":{"conferences":{}}}
    for level in ["FBS","FCS"]:
        for conf, cdata in cfb_structure[level]["conferences"].items():
            teams = cdata.get("teams", [])
            conf_entry = {"teams": []}
            for team in teams:
                if team in known_meta:
                    meta = known_meta[team].copy()
                else:
                    # infer
                    colors = infer_colors(team)
                    offense, defense = infer_schemes(team, conf)
                    prestige = infer_prestige(team, conf)
                    # pick inferred rivals from within conference
                    rivals = pick_rivalries(team, conf, teams)
                    meta = {
                        "colors": colors,
                        "offense_scheme": offense,
                        "defense_scheme": defense,
                        "rivalries": rivals,
                        "prestige": prestige,
                        "notes": "Inferred/heuristic metadata - review for accuracy"
                    }
                # Normalize final dict shape
                entry = {
                    "name": team,
                    "colors": meta.get("colors", ["Unknown"]),
                    "offense_scheme": meta.get("offense_scheme", meta.get("offense", "Unknown")),
                    "defense_scheme": meta.get("defense_scheme", meta.get("defense", "Unknown")),
                    "rivalries": meta.get("rivalries", []),
                    "prestige": int(meta.get("prestige", 50)),
                    "notes": meta.get("notes", "")
                }
                conf_entry["teams"].append(entry)
            out[level]["conferences"][conf] = conf_entry
    return out

# Build dataset
full_metadata = build_full_metadata(CFB_2026, KNOWN_METADATA)

# ---------------------------
# 5) Output file
# ---------------------------
OUT_FILENAME = "CFB_2026_full_metadata.json"
with open(OUT_FILENAME, "w", encoding="utf-8") as f:
    json.dump(full_metadata, f, indent=2, ensure_ascii=False)

print(f"Generated {OUT_FILENAME} in {os.getcwd()}")
print("Note: Major programs have manually-specified metadata; other teams use heuristics/placeholders.")
