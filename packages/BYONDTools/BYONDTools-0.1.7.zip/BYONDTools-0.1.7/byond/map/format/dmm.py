from byond.basetypes import *
from byond.utils import getElapsed, do_profile
# from byond.map import Tile, MapLayer
from byond.map.format.base import BaseMapFormat, MapFormat
import os, sys, logging, itertools, shutil, collections, math
from time import clock

ID_ENCODING_TABLE = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
IET_SIZE = len(ID_ENCODING_TABLE)

def chunker(iterable, chunksize):
    """
    Return elements from the iterable in `chunksize`-ed lists. The last returned
    chunk may be smaller (if length of collection is not divisible by `chunksize`).

    >>> print list(chunker(xrange(10), 3))
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
    """
    i = iter(iterable)
    while True:
        wrapped_chunk = [list(itertools.islice(i, int(chunksize)))]
        if not wrapped_chunk[0]:
            break
        yield wrapped_chunk.pop()
        
def DMMSortAlg(v):
    t = (v.upper(),)
    l = [c.isupper() for c in v]
    l.reverse()
    return t + tuple(l)

@MapFormat('dmm')
class DMMFormat(BaseMapFormat):
    def __init__(self, map):
        BaseMapFormat.__init__(self, map)
        
        self.tileTypes = []
        self.instances = []
        self.oldID2NewID = {}
        
        self.log = logging.getLogger(self.__class__.__name__)
        
        self.filename = 'BUILT-IN?'
        
        self.lineNumber = 0
        
        # Number of duplicates found when loading.
        self.duplicates = 0
        
        # Caches
        self.tileChunk2ID = {}
        self.atomCache = {}
    
        self.atomBorders = {
            '{':'}',
            '"':'"',
            '(':')'
        }
        nit = self.atomBorders.copy()
        for start, stop in self.atomBorders.items():
            if start != stop:
                nit[stop] = None
        self.atomBorders = nit
        self.idlen = 0
        
        self.dump_inherited = False
        
    def Load(self, filename, **kwargs):
        if not os.path.isfile(filename):
            self.log.warn('File ' + filename + " does not exist.")
        self.map.ResetTilestore()
        
        self.filename = filename
        self.lineNumber = 0
        with open(filename, 'r') as f:
            self.log.info('Reading tile types from %s...', self.filename)
            self.consumeTiles(f)
            self.log.info('Reading tile positions...')
            self.consumeTileMap(f)
            
    def consumeDataValue(self, value):
        data = None
        if value[0] in ('"', "'"):
            quote = value[0]
            if quote == '"':
                data = BYONDString(value[1:-1], self.filename, self.lineNumber)
            elif quote == "'":
                data = BYONDFileRef(value[1:-1], self.filename, self.lineNumber)
        elif value == 'null':
            data = BYONDValue(None, self.filename, self.lineNumber)
        else:
            data = BYONDValue(value, self.filename, self.lineNumber)
        return data
    def consumeTileMap(self, f):
        zLevel = None
        y = 0
        z = 0
        inZLevel = False
        width = 0
        height = 0
        
        while True:
            self.lineNumber += 1
            line = f.readline()
            if line == '':
                return
            log_prefix="{}:{}: ".format(self.filename,self.lineNumber)
            # (1,1,1) = {"
            if line.startswith('('):
                coordChunk = line[1:line.index(')')].split(',')
                # print(repr(coordChunk))
                z = int(coordChunk[2])
                inZLevel = True
                y = 0
                width = 0
                height = 0
                
                start = clock()
                #print(log_prefix+' START z={}'.format(z))
                continue
            if line.strip() == '"}':
                zLevel.initial_load=False
                inZLevel = False
                if height == 0:
                    height = y
                # self.map.zLevels[z] = zLevel
                zLevel = None
                self.log.info(' * Added map layer {0} ({1}x{2}, {3})'.format(z, height, width, getElapsed(start)))
                continue
            if inZLevel:
                if zLevel is None:
                    zLevel = self.map.CreateZLevel(height, width)  # , z-1)
                    zLevel.initial_load=True
                    #print(log_prefix+' CREATED z={}'.format(z))
                if width == 0:
                    width = len(line) / self.idlen
                    self.log.debug('Width detected as {}.'.format(width))
                    zLevel.Resize(width, width)
                if width > 255:
                    self.log.warn("%sLine is {} blocks long!", log_prefix, width)
                x = 0
                for chunk in chunker(line.strip(), self.idlen):
                    chunk = ''.join(chunk)
                    tid = self.oldID2NewID[chunk]
                    #if tid == 1:
                    #print('[{},{}] Chunk: {}, tid: {}'.format(x,y,chunk,tid))
                    zLevel.SetTileID(x, y, tid)
                    x += 1
                y += 1
                
    def consumeTiles(self, f):
        index = 0
        self.duplicates = 0
        self.tileChunk2ID = {}
        while True:
            line = f.readline()
            self.lineNumber += 1
            if line.startswith('"'):
                t = self.consumeTile(line)
                #t.ID = index
                t.map = self.map
                t.UpdateHash()
                self.tileTypes += [t]
                self.idlen = max(self.idlen, len(t.origID))
                if t.origID=='':
                    self.log.warning('{}:{}: ERROR: Unable to determine origID.'.format(self.filename,self.lineNumber))
                    sys.exit(1)
                if t.origID == 'aaa':
                    self.map.basetile=t
                    self.log.debug('{}:{}: Loaded tile #{} ({}) as map.basetile.'.format(self.filename,self.lineNumber,t.ID,t.origID))
                self.oldID2NewID[t.origID] = t.ID
                self.tileChunk2ID[self.SerializeTile(t)] = t.ID
                index += 1
                # No longer needed, 2fast.
                # if((index % 100) == 0):
                #   print(index)
            else:
                self.log.info('{} tiles loaded, {} duplicates discarded'.format(index, self.duplicates))
                return 
    
    def consumeTileAtoms(self, line):
        instances = []
        atom_chunks = self.SplitAtoms(line)

        dbg = False
        for atom_chunk in atom_chunks:
            if atom_chunk in self.atomCache:
                atom=self.atomCache[atom_chunk]
                self.log.debug('[CACHED] Adding {} as {}.'.format(atom_chunk,str(atom)))
                instances += [atom]
            else:
                atom = self.consumeAtom(atom_chunk)
                atom.InvalidateHash()
                atom.UpdateMap(self.map)
                self.log.debug('Adding {} ({}) as {}.'.format(atom_chunk,atom.GetHash(),str(atom)))
                self.atomCache[atom_chunk] = atom
                instances += [atom]
            
        return [x.ID for x in instances]
    
    def SplitProperties(self, string):
        o = []
        buf = []
        inString = False
        for chunk in string.split(';'):
            if not inString:
                if '"' in chunk:
                    inString = False
                    pos = 0
                    while(True):
                        pos = chunk.find('"', pos)
                        if pos == -1:
                            break
                        pc = ''
                        if pos > 0:
                            pc = chunk[pos - 1]
                        if pc != '\\':
                            inString = not inString
                        pos += 1
                    if not inString:
                        o += [chunk]
                    else:
                        buf += [chunk]
                else:
                    o += [chunk]
            else:
                if '"' in chunk:
                    o += [';'.join(buf + [chunk])]
                    inString = False
                    buf = []
                else:
                    buf += [chunk]
        return o
    
    def SplitAtoms(self, string):
        ignoreLevel = []
        
        o = []
        buf = ''
        
        string = string.rstrip()
        line_len = len(string)
        for i in xrange(line_len):
            c = string[i]
            pc = ''
            if i > 0:
                pc = string[i - 1]
            
            if c in self.atomBorders and pc != '\\':
                end = self.atomBorders[c]
                if end == c:  # Just toggle.
                    if len(ignoreLevel) > 0:
                        if ignoreLevel[-1] == c:
                            ignoreLevel.pop()
                        else:
                            ignoreLevel.append(c)
                else:
                    if end == None:
                        if len(ignoreLevel) > 0:
                            if ignoreLevel[-1] == c:
                                ignoreLevel.pop()
                    else:
                        ignoreLevel.append(end)
            if c == ',' and len(ignoreLevel) == 0:
                o += [buf]
                buf = ''
            else:
                buf += c
                    
        if len(ignoreLevel) > 0:
            self.log.debug(repr(ignoreLevel))
            sys.exit()
        return o + [buf]
    
    def consumeAtom(self, line):
        if '{' not in line:
            atom = line.strip()
            if atom.endswith('/'):
                self.log.warn('{file}:{line}: Malformed atom: {data} has ending slash.  Stripping slashes from right side.'.format(file=self.filename, line=self.lineNumber, data=atom))
                atom = atom.rstrip('/')
            currentAtom = self.map.GetAtom(atom)
            if currentAtom is not None:
                return currentAtom
            else:
                self.log.error('{file}:{line}: Failed to consumeAtom({data}):  Unable to locate atom.'.format(file=self.filename, line=self.lineNumber, data=line))
                return None
        chunks = line.split('{')
        if len(chunks) < 2:
            self.log.warn('{file}:{line}: Something went wrong in consumeAtom(). line={data}'.format(file=self.filename, line=self.lineNumber, data=line))
        atom = chunks[0].strip()
        if atom.endswith('/'):
            self.log.warn('{file}:{line}: Malformed atom: {data} has ending slash.  Stripping slashes from right side.'.format(file=self.filename, line=self.lineNumber, data=atom))
            atom = atom.rstrip('/')
        currentAtom = self.map.GetAtom(atom)
        if currentAtom is not None:
            currentAtom = currentAtom.copy()
        else:
            return None
        if chunks[1].endswith('}'):
            chunks[1] = chunks[1][:-1]
        property_chunks = self.SplitProperties(chunks[1])
        mapSupplied = []
        for chunk in property_chunks:
            if chunk.endswith('}'):
                chunk = chunk[:-1]
            pparts = chunk.split('=', 1)
            key = pparts[0].strip()
            value = pparts[1].strip()
            if key == '':
                self.log.warn('{file}:{line}: Ignoring property with blank name. (given {chunk})'.format(file=self.filename, line=self.lineNumber, chunk=chunk))
                continue
            data = self.consumeDataValue(value)
            if key not in currentAtom.mapSpecified:
                mapSupplied += [key]
            currentAtom.properties[key] = data
        
        currentAtom.mapSpecified = mapSupplied
                
        # Compare to base
        if True:  # TODO: not (self.readFlags & Map.READ_NO_BASE_COMP):
            base_atom = self.map.GetAtom(currentAtom.path)
            assert base_atom != None
            # for key in base_atom.properties.keys():
            #    val = base_atom.properties[key]
            #    if key not in currentAtom.properties:
            #        currentAtom.properties[key] = val
            for key in currentAtom.properties.iterkeys():
                val = currentAtom.properties[key].value
                if key in base_atom.properties and val == base_atom.properties[key].value:
                    if key in currentAtom.mapSpecified:
                        currentAtom.mapSpecified.remove(key)
                        # print('Removed {0} from atom: Equivalent to base atom!')
                        
        return currentAtom
        
    def consumeTile(self, line, cache=True):
        origid = self.consumeTileID(line)
        return self.consumeTileChunk(line, origID=origid)
    
    def consumeTileChunk(self, line, origID=None, cache=True):
        t = self.map.CreateTile()
        tileChunk = line.strip()[line.index('(') + 1:-1]
        if tileChunk == '':
            self.log.error('{}:{}: MALFORMED TILE CHUNK: {}'.format(self.filename, self.lineNumber, tileChunk))
            
        if cache and origID is not None: 
            #print('CACHING...')
            if tileChunk in self.tileChunk2ID:
                parentID = self.tileChunk2ID[tileChunk]
                self.log.warn('{}:{}: {} duplicate of {}! Installing redirect...'.format(self.filename, self.lineNumber, origID, parentID))
                self.oldID2NewID[origID] = parentID
                self.duplicates += 1
                return self.tileTypes[parentID]
        if origID is not None:
            t.origID = origID
        t.instances = self.consumeTileAtoms(tileChunk)
        t.ID=self.map.UpdateTile(t)
        self.tileChunk2ID[tileChunk]=t.ID
        return t
    
    def consumeTileID(self, line):
        e = line.index('"', 1)
        return line[1:e]
            
    def SerializeAtom(self, atom):
        atomContents = []
        # print(repr(self.mapSpecified))
        if self.dump_inherited:
            for key, val in atom.properties.items():
                atomContents += ['{0} = {1}'.format(key, val)]
        else:
            for i in range(len(atom.mapSpecified)):
                key = atom.mapSpecified[i]
                if key in atom.properties:
                    val = atom.properties[key]
                    atomContents += ['{0} = {1}'.format(key, val)]
        if len(atomContents) > 0:
            return atom.path + '{' + '; '.join(atomContents) + '}'
        else:
            return atom.path
            
    def SerializeTile(self, tile):
        # "aat" = (/obj/structure/grille,/obj/structure/window/reinforced{dir = 8},/obj/structure/window/reinforced{dir = 1},/obj/structure/window/reinforced,/obj/structure/cable{d1 = 2; d2 = 4; icon_state = "2-4"; tag = ""},/turf/simulated/floor/plating,/area/security/prison)
        atoms = []
        for i in xrange(len(tile.instances)):
            atom = self.map.GetInstance(tile.instances[i])
            if atom and atom.path != '':
                atoms += [self.SerializeAtom(atom)]

        return '({atoms})'.format(atoms=','.join(atoms))
    
    def ID2String(self, _id, pad=0):
        o = ''
        while(_id >= len(ID_ENCODING_TABLE)):
            i = _id % IET_SIZE
            o = ID_ENCODING_TABLE[i] + o
            _id -= i
            _id /= IET_SIZE
        o = ID_ENCODING_TABLE[_id] + o
        if pad > len(o):
            o = o.rjust(pad, ID_ENCODING_TABLE[0])
        return o
    
    def String2ID(self, _id):
        o = 0
        for i, c in enumerate(reversed(_id)):
            o += ID_ENCODING_TABLE.index(c) * (IET_SIZE ** i)
        return _id
    
    def AssignTID(self, tile):
        '''
        :param tile Tile:
            Tile to assign ID to.
        '''
        if tile not in self.tileTypes:
            self.tileTypes.append(tile)
        tile.ID = self.tileTypes.index(tile)
        return self.ID2String(tile)
    
    def GetTID(self, tile):
        #print('GetTID: origID: {}'.format(repr(tile.origID)))
        if self.serialize_cleanly and tile.origID != '':
            return self.String2ID(tile.origID)
        else:
            return tile.ID
    
    def Save(self, filename, **kwargs):
        self.filename = filename
        
        self.tileTypes = []
        examined = []
        hashMap = {}
        self.typeMap = {}
        self.type2TID = {}
        self.instances = []
        
        self.serialize_cleanly = kwargs.get('clean', True)
        self.dump_inherited = kwargs.get('inherited', False)
        
        # Preprocess and assign IDs.
        start = clock()
        idlen = 0
        it = self.map.Locations()
        lz = -1
        last_str = None
        start = clock()
        maxid = 0
        for tile in it:
            # print(str(tile))
            if lz != it.z:
                if start:
                    self.log.info('  -> Took {}'.format(getElapsed(start)))
                self.log.info(' * Consolidating level {}...'.format(it.z + 1))
                start = clock()
                lz = it.z
            strt = tile.GetHash()  # str(tile)
            dbg = False
            # if strt == 'e18826df83665059358c177f43f6ac72':
            #    dbg=True
            if last_str == strt:
                # if dbg: print('Continuing: Same as last examined.') 
                continue
            if strt in examined:
                # if dbg: print('Continuing: Hash already examined.')
                last_str = strt
                continue
            # tile.ID = len(examined)
            examined += [strt]
            tid = self.GetTID(tile)
            if tile.origID=='aaa':
                self.log.info('{} -> {}'.format(tile.origID,tid))
            if tid in self.typeMap:
                if hashMap.get(strt, None) == tid:
                    if dbg: self.log.debug('Continuing: TID {} in typeMap, hashes match.'.format(tid))
                    continue
                tile.origID = ''
                tid = len(self.typeMap)
                while tid in self.typeMap:
                    tid += 1

                self.log.info('{} assigned to new TID {}'.format(strt,tid))
            maxid = max(maxid, tid)
            self.typeMap[tid] = (strt, self.SerializeTile(tile))
            last_str = strt
            hashMap[strt] = tid
        
        self.log.info(' * Preprocessing completed in {}'.format(getElapsed(start)))
        idlen = len(self.ID2String(maxid))
        tmpfile = filename + '.tmp'
        self.log.info('Opening {} for write...'.format(tmpfile))
        start = clock()
        with open(tmpfile, 'w') as f:
            for tid in sorted(self.typeMap.keys()):
                stid = self.ID2String(tid, idlen)
                strt, serdata = self.typeMap[tid]
                if serdata == '(/turf/space,/area)':
                    self.log.debug('{} -> {}'.format(tid,stid))
                f.write('"{}" = {}\n'.format(stid, serdata))
                self.type2TID[strt] = stid
            self.log.info(' Wrote types in {}...'.format(getElapsed(start)))
            lap = clock()
            for z in xrange(len(self.map.zLevels)):
                self.log.debug(' Writing z={}...'.format(z))
                f.write('\n(1,1,{0}) = {{"\n'.format(z + 1))
                zlevel = self.map.zLevels[z]
                for y in xrange(zlevel.height):
                    for x in xrange(zlevel.width):
                        tile = self.map.GetTileAt(x, y, z)
                        thash = tile.GetHash()
                        f.write(self.type2TID[thash])
                    f.write("\n")
                f.write('"}\n')
            self.log.info(' Wrote tiles in {}...'.format(getElapsed(lap)))
        if os.path.isfile(filename):
            os.remove(filename)
        os.rename(tmpfile, filename)
        self.log.info('-> {} in {}'.format(filename, getElapsed(start)))
        
