
def init():
    from ruamel.yaml import YAML

    yaml = YAML(typ="rt")
    yaml.default_flow_style = False
    yaml.unicode_supplementary = False
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 85

    return yaml


yaml = init()
