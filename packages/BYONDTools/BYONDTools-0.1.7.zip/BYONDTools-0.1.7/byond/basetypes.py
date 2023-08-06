'''
Created on Nov 6, 2013

@author: Rob
'''
# import logging
AREA_LAYER = 1
TURF_LAYER = 2
OBJ_LAYER = 3
MOB_LAYER = 4
FLY_LAYER = 5

# @formatter:off
COLORS = {
    'aqua':    '#00FFFF',
    'black':   '#000000',
    'blue':    '#0000FF',
    'brown':   '#A52A2A',
    'cyan':    '#00FFFF',
    'fuchsia': '#FF00FF',
    'gold':    '#FFD700',
    'gray':    '#808080',
    'green':   '#008000',
    'grey':    '#808080',
    'lime':    '#00FF00',
    'magenta': '#FF00FF',
    'maroon':  '#800000',
    'navy':    '#000080',
    'olive':   '#808000',
    'purple':  '#800080',
    'red':     '#FF0000',
    'silver':  '#C0C0C0',
    'teal':    '#008080',
    'white':   '#FFFFFF',
    'yellow':  '#FFFF00'
}
# @formatter:on

_COLOR_LOOKUP = {}
    
def BYOND2RGBA(colorstring, alpha=255):
    colorstring = colorstring.strip()
    if colorstring[0] == '#': 
        colorstring = colorstring[1:]
        r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
        r, g, b = [int(n, 16) for n in (r, g, b)]
        return (r, g, b, alpha)
    elif colorstring.startswith('rgb('):
        r, g, b = [int(n.strip()) for n in colorstring[4:-1].split(',')]
        return (r, g, b, alpha)
    else:
        return _COLOR_LOOKUP[colorstring]
    
for name, color in COLORS.items():
    _COLOR_LOOKUP[name] = BYOND2RGBA(color)
    
import re, hashlib, collections
from .utils import eval_expr
REGEX_TABS = re.compile('^(?P<tabs>\t*)') 
class BYONDValue:
    """
    Handles numbers and unhandled types like lists.
    """
    def __init__(self, string, filename='', line=0, typepath='/', **kwargs):
        # : The actual value.
        self.value = string
        
        # : Filename this was found in
        self.filename = filename
        
        # : Line of the originating file.
        self.line = line
        
        # : Typepath of the value.
        self.type = typepath
        
        # : Has this value been inherited?
        self.inherited = kwargs.get('inherited', False)
        
        # : Is this a declaration? (/var)
        self.declaration = kwargs.get('declaration', False)
        
        # : Anything special? (global, const, etc.)
        self.special = kwargs.get('special', None)
        
        # : If a list, what's the size?
        self.size = kwargs.get('size', None)
        
    def copy(self):
        '''Make a clone of this without dangling references.'''
        return BYONDValue(self.value, self.filename, self.line, self.type, declaration=self.declaration, inherited=self.inherited, special=self.special)
    
    def __str__(self):
        if self.value is None:
            return 'null'
        return '{0}'.format(self.value)
        
    def __repr__(self):
        return '<BYONDValue value="{}" filename="{}" line={}>'.format(self.value, self.filename, self.line)
    
    def DumpCode(self, name):
        '''
        Try to dump valid BYOND code for this variable.
        
        .. :param name: The name of this variable.
        '''
        decl = []
        if self.declaration:
            decl += ['var']
        if self.type != '/' and self.declaration:
            decl += self.type.split('/')[1:]
        decl += [name]
        constructed = '/'.join(decl)
        if self.value is not None:
            constructed += ' = {0}'.format(str(self))
        return constructed

class BYONDFileRef(BYONDValue):
    """
    Just to format file references differently.
    """
    def __init__(self, string, filename='', line=0, **kwargs):
        BYONDValue.__init__(self, string, filename, line, '/icon', **kwargs)
        
    def copy(self):
        return BYONDFileRef(self.value, self.filename, self.line, declaration=self.declaration, inherited=self.inherited, special=self.special)
        
    def __str__(self):
        return "'{0}'".format(self.value)
        
    def __repr__(self):
        return '<BYONDFileRef value="{}" filename="{}" line={}>'.format(self.value, self.filename, self.line)

class BYONDString(BYONDValue):
    """
    Correctly formats strings.
    """
    def __init__(self, string, filename='', line=0, **kwargs):
        BYONDValue.__init__(self, string, filename, line, '/', **kwargs)
        
    def copy(self):
        return BYONDString(self.value, self.filename, self.line, declaration=self.declaration, inherited=self.inherited, special=self.special)
        
    def __str__(self):
        return '"{0}"'.format(self.value)
        
    def __repr__(self):
        return '<BYONDString value="{}" filename="{}" line={}>'.format(self.value, self.filename, self.line)

class BYONDList(BYONDValue):
    """
    Correctly formats lists (dict/lists).
    """
    def __init__(self, value, filename='', line=0, **kwargs):
        BYONDValue.__init__(self, value, filename, line, '/', **kwargs)
        
    def copy(self):
        return BYONDString(self.value, self.filename, self.line, declaration=self.declaration, inherited=self.inherited, special=self.special)
        
    def __str__(self):
        vals = []
        if type(self.value) is dict:
            for k,v in self.value.items():
                wk=byond_wrap(k)
                wv=byond_wrap(v)
                vals.append('{} = {}'.format(k,v))
        else:
            vals = self.value
        return 'list({0})'.format(', '.join(vals))
        
    def __repr__(self):
        return '<BYONDList value="{}" filename="{}" line={}>'.format(self.value, self.filename, self.line)
    
class PropertyFlags:
    '''Collection of flags that affect :func:`Atom.setProperty` behavior.'''
    
    # : Property being set should be saved to the map
    MAP_SPECIFIED = 1
    
    # : Property being set should be handled as a string
    STRING = 2
    
    # : Property being set should be handled as a file reference
    FILEREF = 4
    
    # : Property being set should be handled as a value
    VALUE = 8
    
class Atom:
    '''
    An atom is, in simple terms, what BYOND considers a class.
    
    :param string path:
        The absolute path of this atom.  ex: */obj/item/weapon/gun*
    :param string filename:
        The file this atom originated from.
    :param int line:
        The line in the aforementioned file.
    '''

    # : Prints all inherited properties, not just the ones that are mapSpecified.
    FLAG_INHERITED_PROPERTIES = 1
    
    # : writeMap2 prints old_ids instead of the actual IID.
    FLAG_USE_OLD_ID = 2  
    
    def __init__(self, path, filename='', line=0, **kwargs):
        global TURF_LAYER, AREA_LAYER, OBJ_LAYER, MOB_LAYER
        
        # : Absolute path of this atom
        self.path = path
        
        # : Vars of this atom, including inherited vars.
        self.properties = collections.OrderedDict()
        
        # : List of var names that were specified by the map, if atom was loaded from a :class:`byond.map.Map`.
        self.mapSpecified = []
        
        # : Child atoms and procs.
        self.children = {}
        
        # : The parent of this atom.
        self.parent = None
        
        # : The file this atom originated from.
        self.filename = filename
        
        # : Line from the originating file.
        self.line = line
        
        # : Instance ID (maps only).  Used internally, do NOT change.
        self.ID = None
        
        # : Instance ID that was read from the map.
        self.old_id = None
        
        # : Used internally.
        self.ob_inherited = False
        
        # : Loaded from map, but missing in the code. (Maps only)
        self.missing = kwargs.get('missing', False)
        
        # if not self.missing and path == '/area/engine/engineering':
        #    raise Exception('God damnit')
        
        self._hash = None
        
        # : Coords
        self.coords = None
        
        # : Used for masters to track instance locations.
        self.locations = []
        
    def rmLocation(self, map, coord, autoclean=True):
        if coord in self.locations:
            self.locations.remove(coord)
        if autoclean and len(self.locations) == 0:
            map.instances[self.ID] = None  # Mark ready for recovery
            map._instance_idmap.pop(self.GetHash(), None)
    
    def addLocation(self, coord):
        self.locations.append(coord)
        
    def UpdateHash(self, no_map_update=False):
        if self._hash is None:
            self._hash = hashlib.md5(str(self)).hexdigest()

    def UpdateMap(self, map):
        self.UpdateHash()
        map.UpdateAtom(self)
        
    def InvalidateHash(self):
        self._hash = None
        
    def GetHash(self):
        self.UpdateHash()
        return self._hash
    
    def copy(self, toNewMap=False):
        '''
        Make a copy of this atom, without dangling references.
        
        :returns byond.basetypes.Atom
        '''
        new_node = Atom(self.path, self.filename, self.line, missing=self.missing)
        new_node.properties = self.properties.copy()
        new_node.mapSpecified = self.mapSpecified
        if not toNewMap:
            new_node.ID = self.ID
            new_node.old_id = self.old_id
        new_node.UpdateHash()
        # new_node.parent = self.parent
        return new_node
    
    def getProperty(self, index, default=None):
        '''
        Get the value of the specified property.
        
        :param string index:
            The name of the var we want.
        :param mixed default:
            Default value, if the var cannot be found.
        :returns:
            The desired value.
        '''
        prop = self.properties.get(index, None)
        if prop == None:
            return default
        elif prop == 'null':
            return None
        return prop.value
    
    def setProperty(self, index, value, flags=0):
        '''
        Set the value of a property.
        
        In the event the property cannot be found, a new property is added.
        
        This function will attempt to convert python types to BYOND types.  
        Hints can be provided in the form of PropertyFlags given to *flags*.
        
        :param string index:
            The name of the var desired.
        :param mixed value:
            The new value.
        :param int flags:
            Changes value assignment behavior.
            
            +------------------------------------+------------------------------------------------+
            | Flag                               | Effect                                         |
            +====================================+================================================+
            | :attr:`PropertyFlag.MAP_SPECIFIED` | Adds the property to *mapSpecified*, if needed.|
            +------------------------------------+------------------------------------------------+
            | :attr:`PropertyFlag.STRING`        | Forces conversion of value to a BYONDString.   |
            +------------------------------------+------------------------------------------------+
            | :attr:`PropertyFlag.FILEREF`       | Forces conversion of value to a BYONDFileRef.  |
            +------------------------------------+------------------------------------------------+
            | :attr:`PropertyFlag.VALUE`         | Forces conversion of value to a BYONDValue.    |
            +------------------------------------+------------------------------------------------+
            
        :returns:
            The desired value.
        '''
        if flags & PropertyFlags.MAP_SPECIFIED:
            if index not in self.mapSpecified:
                self.mapSpecified += [index]
        if flags & PropertyFlags.VALUE:
            self.properties[index] = BYONDValue(value)
        elif isinstance(value, str) or flags & PropertyFlags.STRING:
            if flags & PropertyFlags.STRING:
                value = str(value)
            self.properties[index] = BYONDString(value)
        elif flags & PropertyFlags.FILEREF:
            if flags & PropertyFlags.FILEREF:
                value = str(value)
            self.properties[index] = BYONDFileRef(value)
        else:
            self.properties[index] = BYONDValue(value)
        
        self.UpdateHash()

    def InheritProperties(self):
        if self.ob_inherited: return
        # debugInheritance=self.path in ('/area','/obj','/mob','/atom/movable','/atom')
        if self.parent:
            if not self.parent.ob_inherited:
                self.parent.InheritProperties()
            for key in sorted(self.parent.properties.keys()):
                value = self.parent.properties[key].copy()
                if key not in self.properties:
                    self.properties[key] = value
                    self.properties[key].inherited = True
                    # if debugInheritance:print('  {0}[{2}] -> {1}'.format(self.parent.path,self.path,key))
        # assert 'name' in self.properties
        self.ob_inherited = True
        for k in self.children.iterkeys():
            self.children[k].InheritProperties()

    def __ne__(self, atom):
        return not self.__eq__(atom)
    
    def __eq__(self, atom):
        if atom == None:
            return False
        # if self.mapSpecified != atom.mapSpecified:
        #    return False
        if self.path != atom.path:
            return False
        return self.properties == atom.properties
    
    def handle_math(self, expr):
        if isinstance(expr, str):
            return eval_expr(expr)
        return expr
        
    def __lt__(self, other):
        if 'layer' not in self.properties or 'layer' not in other.properties:
            return False
        myLayer = 0
        otherLayer = 0
        try:
            myLayer = self.handle_math(self.getProperty('layer', myLayer))
        except ValueError:
            print('Failed to parse {0} as float.'.format(self.properties['layer'].value))
            pass
        try:
            otherLayer = self.handle_math(other.getProperty('layer', otherLayer))
        except ValueError:
            print('Failed to parse {0} as float.'.format(other.properties['layer'].value))
            pass
        return myLayer > otherLayer
        
    def __gt__(self, other):
        if 'layer' not in self.properties or 'layer' not in other.properties: 
            return False
        myLayer = 0
        otherLayer = 0
        try:
            myLayer = self.handle_math(self.getProperty('layer', myLayer))
        except ValueError:
            print('Failed to parse {0} as float.'.format(self.properties['layer'].value))
            pass
        try:
            otherLayer = self.handle_math(other.getProperty('layer', otherLayer))
        except ValueError:
            print('Failed to parse {0} as float.'.format(other.properties['layer'].value))
            pass
        return myLayer < otherLayer
        
    def __str__(self):
        atomContents = []
        for key, val in self.properties.items():
            atomContents += ['{0}={1}'.format(key, val)]
        return '{}{{{}}}'.format(self.path, ';'.join(atomContents))
    
    def dumpPropInfo(self, name):
        o = '{0}: '.format(name)
        if name not in self.properties:
            return o + 'None'
        return o + repr(self.properties[name])
    
    def _DumpCode(self):
        divider = '//' + ((len(self.path) + 2) * '/') + '\n'
        o = divider
        o += '// ' + self.path + '\n'
        o += divider
        
        o += self.path + '\n'
        
        # o += '\t//{0} properties total\n'.format(len(self.properties))
        written=[]
        for name in sorted(self.properties.keys()):
            prop = self.properties[name]
            if prop.inherited: continue
            _type = prop.type
            if not _type.endswith('/'):
                _type += '/'
            prefix = ''
            if prop.declaration:
                prefix = 'var'
            if not prop.declaration:  # and _type == '/':
                _type = ''
            o += '\t{prefix}{type}{name}'.format(prefix=prefix, type=_type, name=name)
            if prop.value is not None:
                o += ' = {value}'.format(value=str(prop))
            o += '\n'
        
        # o += '\n'
        # o += '\t//{0} children total\n'.format(len(self.children))
        procs = ''
        children = ''
        written=[]
        for ck in sorted(self.children.keys()):
            if ck in written:
                continue
            written.append(ck) 
            #co = '\n// ck='+repr(ck)
            co = '\n'
            co += self.children[ck]._DumpCode()
            if isinstance(self.children[ck], Proc):
                procs += co
            else:
                children += co
        o += procs + children
        return o
    
    def DumpCode(self):
        return self._DumpCode()
    
class Proc(Atom):
    def __init__(self, path, arguments, filename='', line=0):
        Atom.__init__(self, path, filename, line)
        self.name = self.figureOutName(self.path)
        self.arguments = arguments
        self.code = []  # (indent, line)
        self.definition = False
        self.origpath = ''
        
    def figureOutName(self, path):
        name = path.split('(')[0]
        return name.split('/')[-1]
        
    def CountTabs(self, line):
        m = REGEX_TABS.match(line)
        if m is not None:
            return len(m.group('tabs'))
        return 0
        
    def AddCode(self, indentLevel, line):
        self.code.append( (indentLevel, line) )
        
    def ClearCode(self):
        self.code = []
        
    def AddBlankLine(self):
        if len(self.code) > 0 and self.code[-1][1] == '':
            return
        self.code += [(0, '')]
        
    def MapSerialize(self, flags=0):
        return None
    
    def InheritProperties(self):
        return
    def getMinimumIndent(self):
        # Find minimum indent level
        for i in range(len(self.code)):
            indent, _ = self.code[i]
            if indent == 0: continue
            return indent
        return 0
    
    def _DumpCode(self):
        args = self.path[self.path.index('('):]
        true_path = self.path[:self.path.index('(')].split('/')
        name = true_path[-1]
        true_path = true_path[:-1]
        if self.definition:
            true_path += ['proc']
        true_path += [name + args]
        o = '\n' + '/'.join(true_path) + '\n'
        min_indent = self.getMinimumIndent()
        # Should be 1, so find the difference.
        indent_delta = 1 - min_indent
        # o += '\t// true_path  = {0}\n'.format(repr(true_path))
        # o += '\t// name       = {0}\n'.format(name)
        # o += '\t// args       = {0}\n'.format(args)
        # o += '\t// definition = {0}\n'.format(self.definition)
        # o += '\t// path       = {0}\n'.format(self.path[:self.path.index('(')])
        # o += '\t// origpath   = {0}\n'.format(self.origpath)
        # o += '\t// min_indent = {0}\n'.format(min_indent)
        # o += '\t// indent_delta = {0}\n'.format(indent_delta)
        for i in range(len(self.code)):
            indent, code = self.code[i]
            indent = max(1, indent + indent_delta)
            if code == '' and i == len(self.code) - 1:
                continue
            if code.strip() == '':
                o += '\n'
            else:
                o += (indent * '\t') + code.strip() + '\n'
        return o

def byond_wrap(value):
    '''Wrap a Python instance with the proper BYONDValue type.
    '''
    T = type(value)
    if T is BYONDValue:
        return value
    if T is str or T is unicode:
        return BYONDString(value)
    elif T is list or T is dict:
        return BYONDList(value)
    else:
        return BYONDValue(value)