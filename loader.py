import os
import yaml

notes_dirs = [
    os.path.join(os.path.dirname(__file__), 'release'),
    os.path.join(os.path.dirname(__file__), 'beta'),
    os.path.join(os.path.dirname(__file__), 'archive'),
]


class ReleaseNotes(object):
    def __init__(self):
        self.settings = {}
        with open(os.path.join(os.path.dirname(__file__), "settings.yml"), "r") as f:
            self.settings = yaml.load(f)

        # Copy notes into the same dict for imports. Release version notes overwrite beta version notes if any
        # version numbers are shared.
        self.notes = self.load_dirs(notes_dirs)

    def organize(self, notelist):
        """Organize the data from the .yml format into the variables that the template context expects."""
        organized_notelist = {}
        for k, n in notelist.iteritems():
            n["new_features"] = []
            n["known_issues"] = []
            n["version"] = k
            n["release"]["version"] = n["version"]
            # Always need at least one unnamed group.
            if "groups" not in n["release"]:
                n["release"]["groups"] = [None]
            # Import system requirements from major version
            if not n["release"].get("system_requirements"):
                import_version = n["release"].get("import_system_requirements")
                if import_version:
                    n["release"]["system_requirements"] = notelist[import_version]["release"]["system_requirements"]
                else:
                    n["release"]["system_requirements"] = ""
            # Push unresolved tags to separate "Known Issues" list.
            for note in n["notes"]:
                if note["tag"] == "unresolved":
                    n["known_issues"].append(note)
                else:
                    n["new_features"].append(note)
            organized_notelist[k] = n
        return organized_notelist

    def load_dirs(self, paths):
        """Load release notes from a list of paths."""
        notes = {}
        for path in paths:
            notefiles = os.listdir(path)
            for notefile in notefiles:
                if notefile.endswith(".yml"):
                    with open(os.path.join(path, notefile), "r") as f:
                        doc = yaml.load(f)
                        notes[os.path.splitext(notefile)[0]] = doc
        sorted_notes = self.organize(notes)
        return sorted_notes


releasenotes = ReleaseNotes()
