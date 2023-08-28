from datetime import date, timedelta


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


def guess_release_date():
    today = date.today()
    guess = today + timedelta(days=2)
    if guess.weekday() == 5:  # Saturday
        guess = guess + timedelta(days=2)  # Shift to Monday
    if guess.weekday() == 6:  # Sunday
        guess = guess + timedelta(days=1)  # Shift to Monday
    assert guess.weekday() < 5

    human_date = guess.strftime("%B %e, %Y")

    return guess.isoformat(), human_date
