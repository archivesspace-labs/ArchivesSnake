import attr, structlog, yaml
from boltons.dictutils import OMD
from os.path import exists, expanduser
from os import environ as env

log = structlog.get_logger(__name__)

def ConfigSources(yaml_path):
    '''Helper method returning an :py:class:`boltons.dictutils.OrderedMultiDict` representing configuration sources (defaults, yaml)'''

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
            log.debug("loaded yaml config", source=yaml_path)
    return omd

@attr.s(slots=True, repr=False)
class ASnakeConfig:
    '''Configuration object.  Essentially a convenience wrapper over an instance of :class:`boltons.dictutils.OrderedMultiDict`'''
    config = attr.ib(converter=ConfigSources, default=attr.Factory(lambda: expanduser(env.get('ASNAKE_CONFIG_FILE', "~/.archivessnake.yml"))))

    def __setitem__(self, k, v):
        return self.config.add(k, v)

    def __getitem__(self, k):
        return self.config[k]

    def update(self, *args, **kwargs):
        '''adds a set of configuration values in 'most preferred' position (i.e. last updated wins). See :meth:`boltons.dictutils.OrderedMultiDict.update_extend`
in the OMD docs'''
        return self.config.update_extend(*args, **kwargs)

    def __repr__(self):
        return "ASnakeConfig({})".format(self.config.todict())
