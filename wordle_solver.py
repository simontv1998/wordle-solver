#!/usr/bin/env python3
"""
Wordle solver using an optimistic entropy strategy.

Optimistic: every guess is drawn from the remaining candidate pool,
so each turn is a live chance to win. Candidates are ranked by
Shannon entropy — the guess that splits the pool most evenly goes first.
"""

import math
import sys
from collections import Counter
from functools import lru_cache

GREEN  = "\033[92m"
YELLOW = "\033[93m"
GRAY   = "\033[90m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
RESET  = "\033[0m"

WORD_LEN    = 5
MAX_GUESSES = 6

# fmt: off
WORDS = [
    "ABACK","ABASH","ABATE","ABBEY","ABHOR","ABIDE","ABODE","ABORT","ABOVE","ABUSE",
    "ABYSS","ACORN","ACRID","ACUTE","ADAGE","ADAPT","ADEPT","ADMIT","ADOBE","ADOPT",
    "ADORE","ADULT","AFTER","AGAPE","AGATE","AGENT","AGILE","AGLOW","AGONY","AGORA",
    "AGREE","AHEAD","AISLE","ALARM","ALBUM","ALERT","ALGAE","ALIEN","ALIGN","ALIKE",
    "ALLAY","ALLOT","ALLOW","ALLOY","ALOFT","ALONE","ALONG","ALOOF","ALOUD","ALTER",
    "AMBER","AMBLE","AMEND","ANGEL","ANGER","ANGLE","ANGRY","ANIME","ANNEX","ANNOY",
    "ANTIC","ANVIL","AORTA","APPLE","APPLY","APRON","ARBOR","ARDOR","ARGUE","ARISE",
    "ARMOR","AROMA","AROSE","ARRAY","ARSON","ASKEW","ATONE","ATTIC","AUDIT","AUGUR",
    "AVIAN","AVOID","AWAKE","AWARD","AWARE","AWFUL","AZURE",
    "BADGE","BADLY","BANDY","BANJO","BARON","BATCH","BATHE","BATTY","BAYOU","BEACH",
    "BEARD","BEAST","BEIGE","BELLE","BELOW","BENCH","BERTH","BEVEL","BIDET","BIGOT",
    "BIKER","BINGE","BISON","BLADE","BLAME","BLAND","BLANK","BLAZE","BLEAK","BLEAT",
    "BLEED","BLESS","BLOKE","BLOOD","BLOOM","BLOWN","BLUNT","BLURT","BLUSH","BOGUS",
    "BOOZE","BOSSY","BOXER","BRACE","BRAID","BRAIN","BRAKE","BRAND","BRAVE","BRAWN",
    "BRAWL","BREAD","BREED","BRIBE","BRIDE","BRINK","BROIL","BROOD","BROOK","BROTH",
    "BROWN","BRUNT","BRUSH","BRUTE","BULKY","BULLY","BUNNY","BURLY","BUSHY","BYWAY",
    "CABIN","CAMEL","CAMEO","CANNY","CAPER","CASTE","CATCH","CATER","CAUSE","CHAFE",
    "CHAFF","CHAIN","CHAIR","CHALK","CHANT","CHAOS","CHASM","CHEAP","CHEAT","CHECK",
    "CHEEK","CHESS","CHEST","CHIDE","CHILD","CHILL","CHIME","CHIMP","CHOIR","CHORE",
    "CHOSE","CHUCK","CHUMP","CIVIC","CIVIL","CLACK","CLAIM","CLAMP","CLANK","CLASH",
    "CLASP","CLEAN","CLEAR","CLERK","CLICK","CLIMB","CLING","CLOAK","CLONE","CLOSE",
    "CLOTH","CLOUD","CLOWN","CLUMP","CLUNG","CLUNK","COACH","COAST","COMET","COMIC",
    "CORAL","CORPS","COURT","COVER","CRAFT","CRANE","CRASH","CRAZE","CREAM","CREEK",
    "CREPT","CREST","CRIMP","CRISP","CROAK","CROWN","CRUSH","CRYPT","CURLY","CURSE",
    "CURVE","CYNIC",
    "DAIRY","DAISY","DECAY","DECOY","DELVE","DENSE","DEPOT","DERBY","DETER","DOUSE",
    "DOWDY","DRAMA","DRAPE","DRAWL","DREAD","DREAM","DREGS","DRESS","DRIED","DRIFT",
    "DRINK","DRIVE","DROLL","DROWN","DRYER","DUCHY","DUSTY","DWARF","DWELL","DWELT",
    "EAGER","EAGLE","EARLY","EARTH","EIGHT","EJECT","ELBOW","ELECT","ELITE","EMBER",
    "EMOTE","EMPOWER","EMPTY","ENDOW","ENJOY","ENNUI","EPOCH","ERODE","ERRANT","EVERY",
    "EXACT","EXERT","EXILE","EXIST","EXPEL","EXTRA",
    "FABLE","FAÇADE","FACET","FAITH","FANCY","FARCE","FAULT","FEAST","FERAL","FETCH",
    "FEVER","FEWER","FIBER","FIEND","FIFTH","FIFTY","FIGHT","FILTH","FINCH","FIORD",
    "FIRST","FLAIL","FLAME","FLANK","FLARE","FLASH","FLASK","FLAWY","FLAIR","FLEET",
    "FLESH","FLICK","FLING","FLIRT","FLOCK","FLOOD","FLOOR","FLOUR","FLOUT","FLOWN",
    "FLUFF","FLUTE","FOAMY","FORCE","FORGE","FORTH","FORUM","FOUND","FRAME","FRAUD",
    "FREAK","FRESH","FRIAR","FROST","FROTH","FROZE","FRUGAL","FRUIT","FRUMP","FULLY",
    "FUNGI","FURRY","FUZZY",
    "GAUDY","GAUZE","GAVEL","GIDDY","GIRTH","GIVEN","GLAND","GLARE","GLAZE","GLEAM",
    "GLEAN","GLIDE","GLINT","GLOAT","GLOOM","GLOSS","GLOVE","GLYPH","GNASH","GNOME",
    "GOLEM","GORGE","GOUGE","GOURD","GRACE","GRADE","GRASP","GRATE","GRAVE","GRAZE",
    "GREED","GREET","GRIEF","GRIME","GRIMY","GRIND","GROAN","GROIN","GROPE","GROUT",
    "GROWL","GRUEL","GRUFF","GRUNT","GUILE","GUISE","GUMMY","GUSTY","GYPSY",
    "HABIT","HARDY","HARSH","HASTE","HASTY","HAUNT","HAVEN","HAVOC","HEADY","HEAVE",
    "HEDGE","HEFTY","HENCE","HERON","HINGE","HIPPO","HOARD","HOARY","HOBBY","HOLLY",
    "HOMER","HONEY","HONOR","HORNY","HORSE","HOTEL","HOUND","HUFFY","HUMAN","HUMUS",
    "HUNCH","HURRY","HUSKY","HYENA","HYPER",
    "ICILY","IDIOM","IGLOO","IMAGE","IMBUE","IMPEL","INANE","INCUR","INEPT","INERT",
    "INFER","INFIX","INGOT","INLAY","INNER","INPUT","INTER","INTRO","IRATE","IVORY",
    "JAUNT","JAZZY","JIFFY","JOUST","JUDGE","JUICY","JUMBO","JUROR",
    "KARMA","KEBAB","KNACK","KNAVE","KNEEL","KNELT","KNIFE","KNOLL","KNELT","KUDOS",
    "LATHE","LEACH","LEAFY","LEARN","LEASE","LEASH","LEDGE","LEECH","LEGAL","LEMON",
    "LEVEL","LEVER","LIGHT","LIMIT","LINEN","LINER","LIVER","LLAMA","LODGE","LOOPY",
    "LORRY","LOTUS","LOVER","LOWLY","LUCID","LUCKY","LUMPY","LUSTY","LYRIC",
    "MAGIC","MANOR","MAPLE","MARCH","MARRY","MARSH","MAXIM","MEALY","MEDAL","MERCY",
    "MERGE","MERIT","METAL","MIDST","MIMIC","MINCE","MIRTH","MISER","MISTY","MIXER",
    "MOCHA","MOGUL","MOLDY","MONEY","MONTH","MOODY","MOPED","MORAL","MOURN","MOUSE",
    "MUDDY","MUMMY","MURAL","MURKY","MUSTY","MYRRH","MYSTIC",
    "NADIR","NAIVE","NASTY","NAVAL","NERVE","NEVER","NICER","NIGHT","NOBLE","NOISE",
    "NYMPH","NOTCH","NOVEL","NURSE","NYMPH",
    "OCTET","OLIVE","ONSET","OPERA","OPTIC","ORBIT","ORDER","ORGAN","OTHEROUGHT",
    "OUGHT","OUNCE","OUTDO","OUTER","OVARY","OVOID","OXIDE",
    "PADDY","PANIC","PAPAL","PARTY","PASTA","PATCH","PATSY","PAUSE","PEACH","PEARL",
    "PESKY","PETAL","PETTY","PHASE","PIANO","PIECE","PILOT","PINCH","PIOUS","PIXEL",
    "PIXIE","PLACE","PLAID","PLAIN","PLANE","PLANK","PLANT","PLATE","PLAZA","PLEAD",
    "PLEAT","PLIED","PLUCK","PLUMB","PLUME","PLUMP","PLUNK","PLUSH","POKER","POLAR",
    "POLKA","POLYP","POPPY","PORCH","POUTY","POWER","PRANK","PRESS","PRICE","PRICK",
    "PRIDE","PRIME","PRIMP","PRISM","PRIVY","PRIZE","PROBE","PRONE","PRONG","PROOF",
    "PROSE","PROWL","PRUDE","PRUNE","PSALM","PUBIC","PULSE","PUNCH","PUPAL","PURGE",
    "PUSHY","PYGMY",
    "QUACK","QUAFF","QUAIL","QUALM","QUART","QUASI","QUEEN","QUERY","QUEUE","QUICK",
    "QUIET","QUIRK","QUOTA","QUOTE",
    "RABBI","RADAR","RADIO","RAINY","RALLY","RAMEN","RANCH","RAVEN","REEDY","REGAL",
    "REIGN","RELAX","RELIC","REPAY","REPEL","RERUN","RESIN","RETRO","REVEL","RIDER",
    "RIFLE","RIGID","RISKY","RIVET","ROAST","ROBIN","ROCKY","ROUGE","ROUGH","ROUND",
    "ROUSE","ROUTE","ROWDY","RULER","RUSTY",
    "SAGAS","SANDY","SAUCY","SAUNA","SAVOR","SAVVY","SCALD","SCALP","SCAM","SCAMP",
    "SCANT","SCARE","SCARF","SCOFF","SCOLD","SCONE","SCOOP","SCOPE","SCOUR","SCRAM",
    "SCREW","SCRUB","SEIZE","SENSE","SERUM","SHAFT","SHAKE","SHAKY","SHALE","SHALL",
    "SHAME","SHAPE","SHARK","SHAWL","SHEEN","SHEER","SHELF","SHELL","SHIFT","SHONE",
    "SHORE","SHRUG","SIEGE","SIREN","SIXTH","SIXTY","SKIMP","SKULK","SKULL","SKUNK",
    "SLACK","SLANT","SLASH","SLATHER","SLEEK","SLEEP","SLEET","SLEPT","SLICK","SLIDE",
    "SLIME","SLIMY","SLING","SLOTH","SLUMP","SLUNG","SLUNK","SLURP","SMACK","SMALL",
    "SMASH","SMEAR","SMELL","SMIRK","SMITE","SMOCK","SMOKE","SMOKY","SNACK","SNAIL",
    "SNAKY","SNARE","SNARL","SNEAK","SNEER","SNIDE","SNIFF","SNORE","SNORT","SNOUT",
    "SOBER","SOGGY","SOLAR","SOMBER","SORRY","SOUTH","SPACE","SPADE","SPARE","SPARK",
    "SPASM","SPAWN","SPEAR","SPECK","SPEED","SPELL","SPILL","SPINE","SPITE","SPLAY",
    "SPOKE","SPOOK","SPOOL","SPORT","SPOUT","SPREE","SPRIG","SPUNK","SQUAD","SQUAT",
    "SQUID","STACK","STAGE","STAIN","STALE","STALL","STAMP","STARE","START","STASH",
    "STATE","STEAL","STEEL","STEEP","STEER","STERN","STICK","STIFF","STILL","STING",
    "STOCK","STOMP","STONE","STOOD","STOOL","STORM","STORY","STOVE","STRAP","STRAY",
    "STRIP","STRUT","STUMP","STUNG","STUNK","STUNT","STYLE","SUAVE","SUGAR","SUITE",
    "SULKY","SUNKEN","SUPER","SWAMP","SWARM","SWATH","SWEAR","SWEAT","SWEPT","SWIFT",
    "SWIPE","SWIRL","SWOOP","SYNOD",
    "TABOO","TACIT","TAFFY","TAINT","TALON","TARDY","TAUNT","TAUPE","TAWNY","TENSE",
    "TEPID","TERRA","TERSE","TESTY","THANK","THATCH","THEFT","THEIR","THICK","THORN",
    "TIDAL","TIGER","TIGHT","TIMER","TIPSY","TITAN","TITHE","TONIC","TOPAZ","TOTAL",
    "TOUGH","TOWEL","TOWER","TRACE","TRACK","TRADE","TRAIL","TRAIN","TRAIT","TRAMP",
    "TRASH","TRAWL","TREAD","TREAT","TREND","TRIAL","TRIBE","TRICK","TRIED","TROVE",
    "TRUCK","TRULY","TRUMP","TRUNK","TRUSS","TRUST","TRUTH","TULIP","TUMOR","TUNER",
    "TUNIC","TWANG","TWEAK","TWICE","TWILL","TWIRL","TWITCH","TYING",
    "UDDER","ULCER","UMBRA","UNCUT","UNDER","UNFIT","UNION","UNITE","UNITY","UNLIT",
    "UNTIL","UNZIP","UPPER","UPSET","URBAN","USHER",
    "VAGUE","VALID","VALOR","VALVE","VAPID","VAPOR","VAULT","VAUNT","VICAR","VIPER",
    "VOMIT","VOTER","VOUCH","VULGAR",
    "WACKY","WATER","WEARY","WEDGE","WEIRD","WHALE","WHEAT","WHEEL","WHERE","WHICH",
    "WHIFF","WHILE","WHINE","WHIRL","WIELD","WINDY","WITCH","WOKEN","WORLD","WORDY",
    "WORST","WORTH","WOULD","WOUND","WRATH","WRING","WRIST","WROTE",
    "YACHT","YIELD","YOUNG","YOUTH","ZAPPY","ZESTY","ZILCH","ZOMBIE",
]
# fmt: on

# Remove any accidental duplicates and non-5-letter entries
WORDS = sorted({w for w in WORDS if len(w) == WORD_LEN and w.isalpha()})


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def score_feedback(guess: str, answer: str) -> str:
    """Return GGYBB-style feedback for a guess against a known answer."""
    result = ["B"] * WORD_LEN
    pool = list(answer)

    for i in range(WORD_LEN):
        if guess[i] == answer[i]:
            result[i] = "G"
            pool[i] = None

    for i in range(WORD_LEN):
        if result[i] == "G":
            continue
        if guess[i] in pool:
            result[i] = "Y"
            pool[pool.index(guess[i])] = None

    return "".join(result)


def filter_candidates(candidates: list, guess: str, feedback: str) -> list:
    return [w for w in candidates if score_feedback(guess, w) == feedback]


# Precomputed feedback table for all (guess, answer) pairs in WORDS.
# Built once at module load; makes entropy O(1) per pair instead of O(WORD_LEN).
_FEEDBACK_TABLE: dict[tuple[str, str], str] = {}


def _build_feedback_table() -> None:
    for g in WORDS:
        for a in WORDS:
            _FEEDBACK_TABLE[(g, a)] = score_feedback(g, a)


def _fb(guess: str, answer: str) -> str:
    return _FEEDBACK_TABLE.get((guess, answer), score_feedback(guess, answer))


def entropy(guess: str, candidates: list) -> float:
    if not candidates:
        return 0.0
    counts = Counter(_fb(guess, c) for c in candidates)
    total = len(candidates)
    return -sum((n / total) * math.log2(n / total) for n in counts.values())


@lru_cache(maxsize=8192)
def _best_guess_cached(candidates_tuple: tuple) -> str:
    """Memoized core: same candidate set always yields the same best guess."""
    candidates = list(candidates_tuple)
    if len(candidates) == 1:
        return candidates[0]
    return max(candidates, key=lambda w: (entropy(w, candidates), w))


def best_guess(candidates: list) -> str:
    """Optimistic pick: highest-entropy candidate. Memoized for speed."""
    return _best_guess_cached(tuple(sorted(candidates)))


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def render_row(guess: str, feedback: str) -> str:
    tiles = []
    for ch, fb in zip(guess, feedback):
        if fb == "G":
            tiles.append(f"{GREEN}{BOLD} {ch} {RESET}")
        elif fb == "Y":
            tiles.append(f"{YELLOW}{BOLD} {ch} {RESET}")
        else:
            tiles.append(f"{GRAY} {ch} {RESET}")
    return "|".join(tiles)


def render_legend() -> str:
    return (
        f"  Feedback key: "
        f"{GREEN}{BOLD}G{RESET}=green (correct)  "
        f"{YELLOW}{BOLD}Y{RESET}=yellow (wrong spot)  "
        f"{GRAY}B{RESET}=gray (absent)"
    )


def parse_feedback(raw: str) -> str | None:
    s = raw.strip().upper()
    if len(s) == WORD_LEN and all(c in "GYB" for c in s):
        return s
    return None


# ---------------------------------------------------------------------------
# Modes
# ---------------------------------------------------------------------------

def interactive_mode():
    """Guide the user through a live Wordle session."""
    candidates = list(WORDS)

    print(f"\n{BOLD}Wordle Solver{RESET} — optimistic strategy")
    print(render_legend())
    print()

    for turn in range(1, MAX_GUESSES + 1):
        suggestion = best_guess(candidates)

        print(f"Turn {turn}/{MAX_GUESSES}  |  {len(candidates)} candidate(s) left")
        print(f"  Suggestion: {CYAN}{BOLD}{suggestion}{RESET}")

        # Accept the suggestion or a custom word
        while True:
            raw = input("  Your guess (Enter = use suggestion): ").strip().upper()
            if not raw:
                guess = suggestion
                break
            if len(raw) == WORD_LEN and raw.isalpha():
                guess = raw
                break
            print(f"  Please enter a {WORD_LEN}-letter word.")

        # Collect feedback
        while True:
            raw_fb = input(f"  Feedback for {BOLD}{guess}{RESET} (e.g. GBYYB): ")
            fb = parse_feedback(raw_fb)
            if fb:
                break
            print("  Invalid — enter exactly 5 characters using G, Y, B.")

        print(f"  {render_row(guess, fb)}")
        print()

        if fb == "G" * WORD_LEN:
            print(f"  {GREEN}{BOLD}Solved in {turn} guess{'es' if turn > 1 else ''}!{RESET}")
            return

        candidates = filter_candidates(candidates, guess, fb)

        if not candidates:
            print("  No candidates match that feedback — please double-check your entries.")
            return

    print(f"  {GRAY}Ran out of guesses. Remaining: {', '.join(candidates)}{RESET}")


def solve_mode(answer: str):
    """Demonstrate the solver against a known answer."""
    answer = answer.upper()
    if answer not in WORDS:
        print(f"'{answer}' is not in the word list. Adding it for this session.")
        WORDS.append(answer)
        WORDS.sort()

    candidates = list(WORDS)

    print(f"\n{BOLD}Solving '{answer}'{RESET} — optimistic strategy")
    print(render_legend())
    print()

    for turn in range(1, MAX_GUESSES + 1):
        guess = best_guess(candidates)
        fb = score_feedback(guess, answer)

        print(f"Turn {turn}/{MAX_GUESSES}  |  {len(candidates)} candidate(s)")
        print(f"  Guess:    {BOLD}{guess}{RESET}")
        print(f"  {render_row(guess, fb)}")
        print()

        if fb == "G" * WORD_LEN:
            print(f"  {GREEN}{BOLD}Solved in {turn} guess{'es' if turn > 1 else ''}!{RESET}")
            return

        candidates = filter_candidates(candidates, guess, fb)

    print(f"  {GRAY}Failed to solve within {MAX_GUESSES} guesses.{RESET}")


def benchmark_mode():
    """Score the solver against every word in the list."""
    totals: list[int] = []
    failures: list[str] = []

    print(f"\n{BOLD}Benchmarking{RESET} on {len(WORDS)} words …")

    for answer in WORDS:
        candidates = list(WORDS)
        for turn in range(1, MAX_GUESSES + 1):
            guess = best_guess(candidates)
            fb = score_feedback(guess, answer)
            if fb == "G" * WORD_LEN:
                totals.append(turn)
                break
            candidates = filter_candidates(candidates, guess, fb)
        else:
            failures.append(answer)

    solved = len(totals)
    total_words = len(WORDS)
    avg = sum(totals) / solved if solved else 0
    dist = Counter(totals)

    print(f"\nSolved {solved}/{total_words}  ({100*solved/total_words:.1f}%)")
    print(f"Average guesses : {avg:.3f}")
    print(f"Distribution    : " + "  ".join(f"{k}:{dist[k]}" for k in sorted(dist)))
    if failures:
        print(f"Failed ({len(failures)}): {', '.join(failures)}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

USAGE = f"""
Usage:
  python wordle_solver.py             — interactive mode (you play Wordle, solver guides)
  python wordle_solver.py solve CRANE — solver demonstrates solving a known answer
  python wordle_solver.py bench       — benchmark solver against all words
  python wordle_solver.py --help      — show this message
"""

def main():
    _build_feedback_table()
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        if not args:
            interactive_mode()
        else:
            print(USAGE)
        return

    cmd = args[0].lower()
    if cmd == "solve":
        if len(args) < 2:
            print("Provide the answer word:  python wordle_solver.py solve CRANE")
            sys.exit(1)
        solve_mode(args[1])
    elif cmd == "bench":
        benchmark_mode()
    else:
        print(f"Unknown command '{args[0]}'.{USAGE}")
        sys.exit(1)


if __name__ == "__main__":
    main()
