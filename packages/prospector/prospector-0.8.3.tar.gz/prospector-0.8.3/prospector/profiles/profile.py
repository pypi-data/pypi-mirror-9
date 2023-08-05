import os
import yaml
from prospector.tools import TOOLS


class ProfileNotFound(Exception):
    def __init__(self, name, profile_path):
        super(ProfileNotFound, self).__init__()
        self.name = name
        self.profile_path = profile_path

    def __repr__(self):
        return "Could not find profile %s; searched in %s" % (self.name, ':'.join(self.filepath))


_EMPTY_DATA = {
    'inherits': [],
    'ignore': [],
    'output-format': None
}


for toolname in TOOLS.keys():
    _EMPTY_DATA[toolname] = {
        'disable': [],
        'enable': [],
        'run': None,
        'options': {}
    }


def load_profiles(names, profile_path):
    if not isinstance(names, (list, tuple)):
        names = (names,)
    profiles = [_load_profile(name, profile_path)[0] for name in names]
    return merge_profiles(profiles)


def _load_content(name, profile_path):
    if name.endswith('.yaml') or name.endswith('.yml'):
        # assume that this is a full path that we can load
        filename = name
    else:
        for path in profile_path:
            filename = os.path.join(path, '%s.yaml' % name)
            if os.path.exists(filename):
                break
        else:
            raise ProfileNotFound(name, profile_path)

    with open(filename) as fct:
        return fct.read()


def from_file(name, profile_path):
    return parse_profile(name, _load_content(name, profile_path))


def _load_profile(name, profile_path, inherits_set=None):
    inherits_set = inherits_set or set()

    profile = parse_profile(name, _load_content(name, profile_path))
    inherits_set.add(profile.name)

    for inherited in profile.inherits:
        if inherited not in inherits_set:
            inherited_profile, sub_inherits_set = _load_profile(
                inherited,
                profile_path,
                inherits_set,
            )
            profile.merge(inherited_profile)
            inherits_set |= sub_inherits_set

    return profile, inherits_set


def parse_profile(name, contents):
    if name.endswith('.yaml'):
        # this was a full path
        name = os.path.splitext(os.path.basename(name))[0]
    data = yaml.safe_load(contents)
    if data is None:
        # this happens if a completely empty YAML file is passed in to
        # parse_profile, for example
        data = dict(_EMPTY_DATA)
    else:
        data = _merge_dict(_EMPTY_DATA, data, dict1_priority=False)
    return ProspectorProfile(name, data)


def _merge_dict(dict1, dict2, dedup_lists=False, dict1_priority=True):
    newdict = {}
    newdict.update(dict1)

    for key, value in dict2.items():
        if key not in dict1:
            newdict[key] = value
        elif value is None and dict1[key] is not None:
            newdict[key] = dict1[key]
        elif dict1[key] is None and value is not None:
            newdict[key] = value
        elif type(value) != type(dict1[key]):
            raise ValueError("Could not merge conflicting types %s and %s" % (
                type(value),
                type(dict1[key]),
            ))
        elif isinstance(value, dict):
            newdict[key] = _merge_dict(
                dict1[key],
                value,
                dedup_lists,
                dict1_priority,
            )
        elif isinstance(value, (list, tuple)):
            newdict[key] = list(set(dict1[key]) | set(value))
        elif not dict1_priority:
            newdict[key] = value

    return newdict


class ProspectorProfile(object):

    def __init__(self, name, profile_dict):
        self.name = name
        self.inherits = profile_dict['inherits']
        self.ignore = profile_dict['ignore']
        self.output_format = profile_dict['output-format']

        for tool in TOOLS.keys():
            setattr(self, tool, profile_dict[tool])

    def to_profile_dict(self):
        thedict = {
            'inherits': self.inherits,
            'ignore': self.ignore,
        }

        for tool in TOOLS.keys():
            thedict[tool] = getattr(self, tool)

    def get_disabled_messages(self, tool_name):
        disable = getattr(self, tool_name)['disable']
        enable = getattr(self, tool_name)['enable']
        return list(set(disable) - set(enable))

    def merge(self, other_profile):
        self.ignore = list(set(self.ignore + other_profile.ignore))
        self.inherits = list(set(self.inherits + other_profile.inherits))
        if other_profile.output_format is not None:
            self.output_format = other_profile.output_format

        for tool in TOOLS.keys():
            merged = _merge_dict(getattr(self, tool), getattr(other_profile, tool))
            setattr(self, tool, merged)

    def is_tool_enabled(self, name):
        return getattr(self, name)['run']


def merge_profiles(profiles):
    merged_profile = profiles[0]
    for profile in profiles[1:]:
        merged_profile.merge(profile)
    return merged_profile
