#!/usr/bin/python3

import sys
import os

from pathlib import Path
from packaging.version import Version

from tools_lib import yaml, notes_template
from ruamel.yaml.comments import CommentedSeq as CS

here = os.path.dirname(__file__)
beta_dir = Path(os.path.join(here, "..", "beta"))
release_dir = Path(os.path.join(here, "..", "release"))
ver_notes_yaml = "{this_esr}.yml"


"""
There are some gremlins lurking in this script, but it gets most of the work done.

This is for generating release notes for a new major ESR-based release (aka 91.0).

Notes will need to be rearranged into the proper order. They also need to be checked
to make sure that they actually apply. For example, for ESR91, regression fixes that
were caused by the change to js-smtp/js-mime and such are not included.

Example:
    ./tools/major_esr_notes.py 115 128 2024-07-09
"""


class RelNote:
    def __init__(self, bugs, tag, note_text):
        bugs.sort()
        self.bugs = bugs
        self.tag = tag
        self.note = note_text

    @property
    def output(self):
        return {"note": self.note, "tag": self.tag, "bugs": self.bugs}


def load_notes(previous, current, release_date):
    uplift_bugs = []
    beta_notes = {}
    new_notes = []

    min_version = Version("{}.0".format(previous))
    max_version = Version("{}.0".format(current))

    # Get the list of bugs that were uplifted during the previous cycle.
    previous_glob = "{}.*.yml".format(previous)
    previous_notes_files = list(release_dir.glob(previous_glob))
    prev_file_names = sorted([os.path.basename(p) for p in previous_notes_files])
    print(f"Using files for finding uplifts: {prev_file_names}")

    for _file in previous_notes_files:
        with _file.open() as fp:
            doc = yaml.load(fp)

        ver_notes = doc["notes"]
        for note in ver_notes:
            if note["tag"] == "unresolved":
                continue
            if "bugs" not in note:
                continue
            else:
                uplift_bugs.extend(note["bugs"])

    note_files = os.listdir(beta_dir)
    for _file in note_files:
        if not _file.endswith("beta.yml"):
            continue
        version = Version(_file[:-8])
        # Exclude the previous esr's beta and lower and anything newer than
        # the current esr
        if version <= min_version:
            continue
        if version > max_version:
            continue

        with open(os.path.join(beta_dir, _file), "r") as fp:
            doc = yaml.load(fp)
            beta_notes[_file[:-8]] = doc

    versions = sorted([Version(v) for v in beta_notes.keys()])

    # more bugs to exclude based on [Supernova3p] whiteboard
    EXCLUDE = [
        1803272, 1806938, 1809896, 1811646, 1812209, 1812391, 1812403, 1812413,
        1812868, 1813367, 1813371, 1813492, 1813955, 1813959, 1814300, 1814319,
        1814320, 1814321, 1814574, 1814748, 1814956, 1815026, 1815028, 1815096,
        1815144, 1815210, 1815291, 1815407, 1815489, 1815584, 1815607, 1815645,
        1815944, 1816008, 1816041, 1816294, 1816295, 1816297, 1816351, 1816352,
        1816485, 1816610, 1816612, 1816741, 1816788, 1816797, 1816798, 1816799,
        1816801, 1816804, 1816807, 1816808, 1816809, 1816811, 1816812, 1816813,
        1816814, 1816816, 1816817, 1816818, 1816820, 1816822, 1816824, 1817030,
        1817083, 1817085, 1817095, 1817099, 1817109, 1817151, 1817153, 1817157,
        1817218, 1817292, 1817367, 1817374, 1817402, 1817414, 1817462, 1817508,
        1817605, 1817624, 1817670, 1817673, 1817687, 1817731, 1817836, 1817867,
        1817869, 1817870, 1817871, 1817872, 1817878, 1817879, 1817890, 1817897,
        1817907, 1817908, 1817909, 1817911, 1817913, 1817914, 1817915, 1817917,
        1817918, 1817938, 1817947, 1818060, 1818066, 1818086, 1818117, 1818118,
        1818165, 1818166, 1818169, 1818191, 1818201, 1818204, 1818326, 1818330,
        1818333, 1818592, 1818683, 1818946, 1818950, 1819005, 1819010, 1819013,
        1819089, 1819103, 1819104, 1819107, 1819137, 1819182, 1819195, 1819197,
        1819201, 1819214, 1819220, 1819236, 1819248, 1819276, 1819277, 1819281,
        1819288, 1819291, 1819292, 1819338, 1819344, 1819349, 1819383, 1819433,
        1819499, 1819508, 1819546, 1819548, 1819552, 1819572, 1819604, 1819607,
        1819610, 1819611, 1819612, 1819631, 1819633, 1819765, 1819777, 1819780,
        1819788, 1819795, 1819840, 1819856, 1819869, 1819916, 1819953, 1819963,
        1819993, 1819999, 1820004, 1820006, 1820009, 1820023, 1820052, 1820057,
        1820077, 1820167, 1820188, 1820201, 1820220, 1820262, 1820329, 1820379,
        1820383, 1820394, 1820421, 1820422, 1820423, 1820486, 1820500, 1820607,
        1820698, 1820700, 1820786, 1820794, 1820872, 1820898, 1821014, 1821111,
        1821115, 1821141, 1821205, 1821234, 1821235, 1821241, 1821382, 1821465,
        1821484, 1821518, 1821519, 1821573, 1821574, 1821617, 1821626, 1821667,
        1821711, 1821756, 1821802, 1821804, 1821808, 1821894, 1821902, 1821915,
        1821933, 1821946, 1821947, 1821999, 1822048, 1822057, 1822064, 1822224,
        1822226, 1822227, 1822239, 1822286, 1822332, 1822339, 1822389, 1822422,
        1822441, 1822475, 1822523, 1822525, 1822537, 1822607, 1822622, 1822655,
        1822705, 1822807, 1822815, 1822838, 1822841, 1822910, 1822991, 1822994,
        1823019, 1823033, 1823038, 1823055, 1823066, 1823068, 1823070, 1823072,
        1823091, 1823112, 1823113, 1823124, 1823125, 1823129, 1823130, 1823138,
        1823146, 1823169, 1823179, 1823182, 1823183, 1823186, 1823252, 1823254,
        1823264, 1823349, 1823378, 1823389, 1823448, 1823486, 1823517, 1823544,
        1823546, 1823548, 1823577, 1823609, 1823628, 1823637, 1823652, 1823672,
        1823734, 1823737, 1823748, 1823792, 1823816, 1823830, 1823858, 1823882,
        1823976, 1823978, 1824001, 1824018, 1824020, 1824067, 1824078, 1824106,
        1824122, 1824144, 1824156, 1824184, 1824210, 1824272, 1824274, 1824289,
        1824290, 1824313, 1824336, 1824422, 1824454, 1824478, 1824536, 1824555,
        1824593, 1824623, 1824692, 1824756, 1824767, 1824880, 1824954, 1824969,
        1825012, 1825089, 1825150, 1825158, 1825166, 1825184, 1825191, 1825226,
        1825227, 1825240, 1825254, 1825258, 1825265, 1825268, 1825281, 1825369,
        1825372, 1825393, 1825430, 1825436, 1825499, 1825513, 1825588, 1825624,
        1825627, 1825685, 1825864, 1825870, 1825919, 1825924, 1825925, 1825948,
        1825963, 1825993, 1826009, 1826148, 1826150, 1826167, 1826218, 1826342,
        1826406, 1826441, 1826443, 1826626, 1826627, 1826633, 1826737, 1826831,
        1826887, 1826925, 1826939, 1826999, 1827003, 1827198, 1827212, 1827218,
        1827251, 1827254, 1827257, 1827261, 1827445, 1827464, 1827514, 1827654,
        1827685, 1827700, 1827743, 1827755, 1827833, 1827930, 1827946, 1827962,
        1828056, 1828136, 1828284, 1828301, 1828330, 1828331, 1828339, 1828341,
        1828348, 1828351, 1828352, 1828359, 1828457, 1828499, 1828530, 1828624,
        1828636, 1828664, 1828725, 1828830, 1828914, 1829055, 1829065, 1829095,
        1829099, 1829149, 1829194, 1829343, 1829400, 1829491, 1829536, 1829565,
        1829632, 1829785, 1829808, 1829867, 1829948, 1829974, 1830004, 1830224,
        1830242, 1830306, 1830468, 1830518, 1830550, 1830559, 1830578, 1830594,
        1830600, 1830609, 1830698, 1830830, 1831152, 1831159, 1831190, 1831224,
        1831303, 1831464, 1831465, 1831584, 1831615, 1831667, 1831716, 1831717,
        1831759, 1831766, 1831969, 1832011, 1832050, 1832051, 1832379, 1832383,
        1832471, 1832545, 1832662, 1832698, 1832940, 1832942, 1832943, 1833017,
        1833041, 1833042, 1833134, 1833145, 1833275, 1833305, 1833472, 1833565,
        1833675, 1833684, 1833709, 1833764, 1833804, 1833845, 1834221, 1834397,
        1834479, 1834606, 1834664, 1834705, 1834723, 1834826, 1834893, 1834952,
        1834987, 1835026, 1835173, 1835358, 1835498, 1835499, 1835601, 1835602,
        1835619, 1835683, 1835974, 1836084, 1836111, 1836114, 1836145, 1836361,
        1836391, 1836423, 1836488, 1836596, 1836846, 1837041, 1837438, 1837441,
        1837594, 1837677, 1837831, 1838190, 1838347, 1838449, 1838489, 1838770,
        1839472, 1840007, 1840087, 1840940, 1840943
        ]


    for ver_str in [str(v) for v in versions]:
        ver_notes = beta_notes[ver_str]["notes"]
        for note in ver_notes:
            if note["tag"] == "unresolved":
                continue
            if "bugs" not in note:
                continue

            # Exclude anything that looks like it was uplifted or in exclude list
            if not any(elem in uplift_bugs or elem in EXCLUDE for elem in note["bugs"]):
                rel_note = RelNote(note["bugs"], note["tag"], note["note"])
                new_notes.append(rel_note)

    new_yaml = yaml.load(notes_template.TMPL_HEADER)
    new_yaml["release"]["text"] = notes_template.TMPL_RELEASE_TEXT[current]
    new_yaml["release"][
        "import_system_requirements"
    ] = notes_template.REQUIREMENTS_IMPORT[current]
    new_yaml["release"]["release_date"] = release_date

    notes_sequence = CS()
    note_counter = 0

    for tag_name in ["new", "changed", "fixed"]:
        tag_notes = [note for note in new_notes if note.tag == tag_name]
        for note in tag_notes:
            notes_sequence.append(note.output)
            notes_sequence.yaml_set_comment_before_after_key(
                note_counter, "{}\n".format(tag_name.capitalize()), 2
            )
            note_counter += len(tag_notes)

    new_yaml["notes"] = notes_sequence

    this_esr = "{}.0".format(current)
    out_yaml = ver_notes_yaml.format(this_esr=this_esr)
    with open(out_yaml, "w") as fp:
        yaml.dump(new_yaml, fp)

    print("Wrote notes to {}.".format(out_yaml))


if __name__ == "__main__":
    previous_esr = sys.argv[1]
    current_esr = sys.argv[2]
    release_date = sys.argv[3]
    load_notes(previous_esr, current_esr, release_date)
