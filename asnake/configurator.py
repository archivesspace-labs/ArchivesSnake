import attr, yaml

from boltons.dictutils import OMD
from os.path import exists, expanduser
from os import environ as env



def ConfigSources(yaml_path):
    '''Helper method returning an :py:class:`boltons.dictutils.OrderedMultiDict` representing configuration sources (defaults, yaml)'''
    omd = OMD()
    yaml_path = expanduser(yaml_path)

    # Fallback to defaults for local devserver
    omd.update({
        'baseurl'         : 'http://localhost:4567',
        'username'        : 'admin',
        'password'        : 'admin',
        'session_header_name': 'X-ArchivesSpace-Session',
        'retry_with_auth' : True,

    })


    if exists(yaml_path):
        with open(yaml_path, 'r') as f:
            omd.update_extend(yaml.safe_load(f))
    return omd

@attr.s(slots=True, repr=False)
class ASnakeConfig:
    '''Configuration object.  Essentially a convenience wrapper over an instance of :class:`boltons.dictutils.OrderedMultiDict`'''
    config = attr.ib(converter=ConfigSources, default=attr.Factory(lambda: env.get('ASNAKE_CONFIG_FILE', "~/.archivessnake.yml")))

    def __setitem__(self, k, v):
        return self.config.add(k, v)

    def __getitem__(self, k):
        return self.config[k]

    def get(self, k, default=None):
        return self.config.get(k, default)

    def __contains__(self, k):
        return k in self.config

    def update(self, *args, **kwargs):
        '''adds a set of configuration values in 'most preferred' position (i.e. last updated wins). See :meth:`boltons.dictutils.OrderedMultiDict.update_extend`
in the OMD docs'''
        return self.config.update_extend(*args, **kwargs)

    def __repr__(self):
        return "ASnakeConfig({})".format(self.config.todict())
