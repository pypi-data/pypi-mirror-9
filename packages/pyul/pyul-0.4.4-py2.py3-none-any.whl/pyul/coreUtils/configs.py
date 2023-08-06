import yaml
import json
import pprint
from .common import synthesize, get_user_temp_dir
from .compare import ComparableMixin
from .dotifydict import DotifyDict
from ..xmlUtils import parseToDict, unparseFromDict
from ..importUtils import ImportModule
from ..support import Path

__all__ = ['Config','YAMLConfig','JSONConfig','XMLConfig','PythonConfig']   


class Config(ComparableMixin, DotifyDict):
    """
    A utility class for representing a format as a dictionary of nested data.
    """

    def __init__(self, filepath=''):
        filepath = Path(filepath)
        if filepath.is_dir():
            filepath = get_user_temp_dir().joinpath('temp.dat')
        synthesize(self, 'filepath', filepath)
        self.read()

    def _cmpkey(self):
        return tuple(self._get_data().values())

    def _ignore_keys(self):
        return ['_filepath']

    def _get_data(self, data=None):
        if data is None:
            data = self
        output = {}
        ignore_keys = self._ignore_keys()
        for k, v in [(k,v) for k,v in data.items() if k not in ignore_keys]:
            if isinstance(v, DotifyDict):
                output[k] = self._get_data(v)
            else:
                output[k] = v
        return output

    def update(self, u):
        for k, v in u.iteritems():
            if k in self._ignore_keys():
                continue
            if isinstance(v, DotifyDict):
                d = getattr(self, k)
                self[k] = d.update(v)
            else:
                self[k] = u[k]
        return self

    def load(self, data):
        parsed_data = self.parse(data)
        if not isinstance(parsed_data, dict):
            raise ValueError('Unable to load data.  Not properly formated or parser failed to return a dict.')
        for k, v in parsed_data.items():
            try:
                setattr(self, k, DotifyDict(v))
            except:
                setattr(self, k, v)

    def read(self):
        if not self._filepath.exists():
            return
        with open(str(self._filepath)) as fh:
            data = fh.read()
        self.load(data)

    def dump(self):
        return self.unparse(self._get_data())

    def write(self):
        '''Writes the dict data to the file'''
        with open(str(self._filepath),'wb') as fh :
            fh.write(self.dump())

    def pprint(self):
        pprint.pprint(self._get_data())

    def parse(self, data):
        raise NotImplementedError

    def unparse(self, data):
        raise NotImplementedError


class YAMLConfig(Config):
    """
    Class for representing yaml data as a nested dictionary
    """
    def parse(self, data):
        return yaml.safe_load(data)

    def unparse(self, data):
        return yaml.safe_dump(data, default_flow_style=False)


class JSONConfig(Config):
    """
    Class for representing json data as a nested dictionary
    """
    def parse(self, data):
        return json.loads(data)

    def unparse(self, data):
        return json.dumps(data,
                          sort_keys=True,
                          indent=4)


class XMLConfig(Config):
    """
    Class for representing xml data as a nested dictionary
    """
    def parse(self, data):
        return parseToDict(data)

    def unparse(self, data):
        return unparseFromDict(data)


class PythonConfig(Config):
    def read(self):
        mod = ImportModule(str(self._filepath))
        self.load(mod.__dict__)

    def parse(self, data):
        output = dict()
        for name, value in data.items():
            if name.startswith('__'):
                continue
            output[name.lower()] = value
        return output


if __name__ == '__main__':    
    yaml_config = YAMLConfig('/Users/kyle.rockman/data.yaml')
    json_config = JSONConfig('/Users/kyle.rockman/data.json')
    xml_config = XMLConfig('/Users/kyle.rockman/data.xml')
    yaml_config.pprint()
    json_config.pprint()
    xml_config.pprint()
    yaml_config.write()
    json_config.write()
    xml_config.write()
