'''
Created on Dec 28, 2014

@author: Rob
'''
from .base import BaseMapRenderer
class FullDefMapRenderer(BaseMapRenderer):
                
    def renderAtom(self, atom, basedir, skip_alpha=False):
        if 'icon' not in atom.properties:
            logging.critical('UNKNOWN ICON IN ATOM #{0} ({1})'.format(atom.ID, atom.path))
            logging.info(atom.MapSerialize())
            logging.info(atom.MapSerialize(Atom.FLAG_INHERITED_PROPERTIES))
            return None
        # else:
        #    logging.info('Icon found for #{}.'.format(atom.ID))
        
        dmi_file = atom.properties['icon'].value
        
        if dmi_file is None:
            return None
        
        # Grab default icon_state ('') if we can't find the one defined.
        state = atom.getProperty('icon_state', '')
        
        direction = SOUTH
        if 'dir' in atom.properties:
            try:
                direction = int(atom.properties['dir'].value)
            except ValueError:
                logging.critical('FAILED TO READ dir = ' + repr(atom.properties['dir'].value))
                return None
        
        icon_key = '{0}|{1}|{2}'.format(dmi_file, state, direction)
        frame = None
        pixel_x = 0
        pixel_y = 0
        if icon_key in _icons:
            frame, pixel_x, pixel_y = _icons[icon_key]
        else:
            dmi_path = os.path.join(basedir, dmi_file)
            dmi = None
            if dmi_path in _dmis:
                dmi = _dmis[dmi_path]
            else:
                try:
                    dmi = DMI(dmi_path)
                    dmi.loadAll()
                    _dmis[dmi_path] = dmi
                except Exception as e:
                    print(str(e))
                    for prop in ['icon', 'icon_state', 'dir']:
                        print('\t{0}'.format(atom.dumpPropInfo(prop)))
                    pass
            if dmi.img is None:
                logging.warning('Unable to open {0}!'.format(dmi_path))
                return None
            
            if dmi.img.mode not in ('RGBA', 'P'):
                logging.warn('{} is mode {}!'.format(dmi_file, dmi.img.mode))
                
            if direction not in IMAGE_INDICES:
                logging.warn('Unrecognized direction {} on atom {}!'.format(direction, str(atom)))
                direction = SOUTH  # DreamMaker property editor shows dir = 2.  WTF?
                
            frame = dmi.getFrame(state, direction, 0)
            if frame == None:
                # Get the error/default state.
                frame = dmi.getFrame("", direction, 0)
            
            if frame == None:
                return None
            
            if frame.mode != 'RGBA':
                frame = frame.convert("RGBA")
                
            pixel_x = 0
            if 'pixel_x' in atom.properties:
                pixel_x = int(atom.properties['pixel_x'].value)
                
            pixel_y = 0
            if 'pixel_y' in atom.properties:
                pixel_y = int(atom.properties['pixel_y'].value)
            
            _icons[icon_key] = (frame, pixel_x, pixel_y)
                
        # Handle BYOND alpha and coloring
        c_frame = frame
        alpha = int(atom.getProperty('alpha', 255))
        if skip_alpha:
            alpha = 255
        color = atom.getProperty('color', '#FFFFFF')
        if alpha != 255 or color != '#FFFFFF':
            c_frame = tint_image(frame, BYOND2RGBA(color, alpha))
        return c_frame
    
    def RenderMap(self, filename_tpl, basedir='.', renderflags=0, z=None, **kwargs):
        '''
        Instead of generating on a tile-by-tile basis, this creates a large canvas and places
        each atom on it after sorting layers.  This resolves the pixel_(x,y) problem.
        '''
        if z is None:
            for z in range(len(self.zLevels)):
                self.Render(filename_tpl, basedir, renderflags, z, **kwargs)
            return
        
        self.selectedAreas = ()
        skip_alpha = False
        render_types = ()
        if 'area' in kwargs:
            self.selectedAreas = kwargs['area']
        if 'render_types' in kwargs:
            render_types = kwargs['render_types']
        if 'skip_alpha' in kwargs:
            skip_alpha = kwargs['skip_alpha']
            
        print('Checking z-level {0}...'.format(z))
        instancePositions = {}
        for y in range(self.map.zLevels[z].height):
            for x in range(self.map.zLevels[z].width):
                t = self.map.zLevels[z].GetTile(x, y)
                # print('*** {},{}'.format(x,y))
                if t is None:
                    continue
                if len(self.selectedAreas) > 0:
                    renderThis = True
                    for atom in t.GetAtoms():
                        if atom.path.startswith('/area'):
                            if  atom.path not in self.selectedAreas:
                                renderThis = False
                    if not renderThis: continue
                for atom in t.GetAtoms():
                    if atom is None: continue
                    iid = atom.ID
                    if atom.path.startswith('/area'):
                        if  atom.path not in self.selectedAreas:
                            continue
                            
                    # Check for render restrictions
                    if len(render_types) > 0:
                        found = False
                        for path in render_types:
                            if atom.path.startswith(path):
                                found = True
                        if not found:
                            continue

                    # Ignore /areas.  They look like ass.
                    if atom.path.startswith('/area'):
                        if not (renderflags & MapRenderFlags.RENDER_AREAS):
                            continue
                    
                    # We're going to turn space black for smaller images.
                    if atom.path == '/turf/space':
                        if not (renderflags & MapRenderFlags.RENDER_STARS):
                            continue
                        
                    if iid not in instancePositions:
                        instancePositions[iid] = []
                        
                    # pixel offsets
                    '''
                    pixel_x = int(atom.getProperty('pixel_x', 0))
                    pixel_y = int(atom.getProperty('pixel_y', 0))
                    t_o_x = int(round(pixel_x / 32))
                    t_o_y = int(round(pixel_y / 32))
                    pos = (x + t_o_x, y + t_o_y)
                    '''
                    pos = (x, y)
                    
                    instancePositions[iid].append(pos)
                    
                    t = None
        
        if len(instancePositions) == 0:
            return
        
        print(' Rendering...')
        levelAtoms = []
        for iid in instancePositions:
            levelAtoms += [self.GetInstance(iid)]
        
        pic = Image.new('RGBA', ((self.zLevels[z].width + 2) * 32, (self.zLevels[z].height + 2) * 32), "black")
            
        # Bounding box, used for cropping.
        bbox = [99999, 99999, 0, 0]
            
        # Replace {z} with current z-level.
        filename = filename_tpl.replace('{z}', str(z))
        
        pastes = 0
        for atom in sorted(levelAtoms, reverse=True):
            if atom.ID not in instancePositions:
                levelAtoms.remove(atom)
                continue
            icon = self.renderAtom(atom, basedir, skip_alpha)
            if icon is None:
                levelAtoms.remove(atom)
                continue
            for x, y in instancePositions[atom.ID]:
                new_bb = self.getBBoxForAtom(x, y, atom, icon)
                # print('{0},{1} = {2}'.format(x, y, new_bb))
                # Adjust cropping bounds 
                if new_bb[0] < bbox[0]:
                    bbox[0] = new_bb[0]
                if new_bb[1] < bbox[1]:
                    bbox[1] = new_bb[1]
                if new_bb[2] > bbox[2]:
                    bbox[2] = new_bb[2]
                if new_bb[3] > bbox[3]:
                    bbox[3] = new_bb[3]
                pic.paste(icon, new_bb, icon)
                pastes += 1
            icon = None  # Cleanup
            levelAtoms.remove(atom)
        
        levelAtoms = None
        instancePositions = None
            
        if len(self.selectedAreas) == 0:            
            # Autocrop (only works if NOT rendering stars or areas)
            # pic = trim(pic) # FIXME: MemoryError on /vg/.
            #pic = pic  # Hack
            pic = pic.crop(bbox) # Hack
        else:
            # if nSelAreas == 0:
            #    continue
            pic = pic.crop(bbox)
        
        if pic is not None:
            # Saev
            filedir = os.path.dirname(os.path.abspath(filename))
            if not os.path.isdir(filedir):
                os.makedirs(filedir)
            print(' -> {} ({}x{}) - {} objects'.format(filename, pic.size[0], pic.size[1], pastes))
            pic.save(filename, 'PNG')
