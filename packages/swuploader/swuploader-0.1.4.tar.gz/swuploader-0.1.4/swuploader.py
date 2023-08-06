import base64
import glob
import os

__version__ = "0.1.4"


def parse_settings(settings_filename):
    settings_filename = os.path.abspath(settings_filename)
    name, ext = os.path.splitext(os.path.basename(settings_filename))
    settings = {
        "name": name,
        "hasRightsToModel": True,
        "acceptTermsAndConditions": True,
        "materials": {},
    }
    with open(settings_filename) as fp:
        for line in fp:
            name, _, value = line.strip("\r\n").partition("=")

            if value.lower() == "false":
                value = False
            elif value.lower() == "true":
                value = True

            if name == "file":
                dirname = os.path.dirname(settings_filename)
                value = os.path.abspath(os.path.join(dirname, value))
                filename = os.path.basename(value)
                settings["fileName"] = filename
            elif name.startswith("material."):
                _, _, mat_id = name.partition(".")
                settings["materials"][int(mat_id)] = {
                    "markup": float(value),
                    "isActive": True,
                }
                continue
            elif name == "categories":
                value = [int(c) for c in value.split(",")]
            elif name == "tags":
                value = [t for t in value.split(",")]

            settings[name] = value
    return settings_filename, settings


def get_models(dir_name=None):
    if dir_name is None:
        dir_name = os.getcwd()
    pattern = "%s/*.ini" % (dir_name, )
    for settings_filename in glob.iglob(pattern):
        yield parse_settings(settings_filename)


def upload_model(settings, client):
    if not settings.get("file"):
        return False

    with open(settings["file"], "rb") as fp:
        settings["file"] = base64.b64encode(fp.read())

    return client.add_model(settings)
