from boltons.dictutils import OMD
import yaml, attr
from os.path import exists, expanduser
from os import environ as env

def ConfigSources(yaml_path):
    omd = OMD()
    # Fallback to defaults for local devserver
    omd.update({
        'baseurl': 'http://localhost:4567',
        'username': 'admin',
        'password': 'admin'
    })

    if exists(yaml_path):
        with open(yaml_path, 'r') as f:
            omd.update_extend(yaml.safe_load(f))
    return omd

@attr.s(slots=True, repr=False)
class ASnakeConfig:
    config = attr.ib(converter=ConfigSources, default=expanduser(env.get('ASNAKE_CONFIG_FILE', "~/.archivessnake.yml")))

    def __setitem__(self, k, v):
        return self.config.add(k, v)

    def __getitem__(self, k):
        return self.config[k]

    def update(self, *args, **kwargs):
        return self.config.update_extend(*args, **kwargs)

    def __repr__(self):
        return "ASnakeConfig({})".format(self.config.todict())
