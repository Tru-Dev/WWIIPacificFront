# WWII Pacific Front - sprite_extension.py
# (C) 2021 Jesus Trujillo, Delaney Siggia, Calvin Guela, Anthony Jaimes, Rocco Carrozza
'''
This module offers two distinct functionalities: nestable groups (and sprites to
go along with them) and behavior groups.

`NesterSprites` can only be in one `NestingGroup`, which is why the `BehaviorGroup` class was
implemented. They act like a regular `pygame.sprite.Group`, but do not implement rendering
and can hold as many sprites as needed.
'''

from collections import defaultdict
from typing import DefaultDict, Dict, Iterable, List, Optional, Union
from enum import IntEnum
import warnings

import pygame
import pygame.event
import pygame.key
import pygame.display
import pygame.freetype
import pygame.sprite

from .misc_utils import TypeWarning


class DirtyEnum(IntEnum):
    '''
    Interchangeable with normal integer Dirty values.
    Use this for readability.
    '''
    NOT_DIRTY = 0
    DIRTY = 1
    ALWAYS_DIRTY = 2

class NestingRecursionError(Exception):
    '''
    Raised when attempting to recursively nest groups:
    ```py
    g = NestingGroup(parent_group=NestingGroup())
    g.add(g.parent) # bad, raises NestingRecursionError
    ```
    '''

class NesterSprite(pygame.sprite.Sprite):
    '''
    A version of `DirtySprite` optimized for NestingGroups.
    It inherits from normal `Sprite` but implements much of the same dirtying functionality.

    One difference is that one `NesterSprite` can only belong to one `NestingGroup`, while
    `NestingGroup`s can still have as many `NesterSprite`s as needed.
    '''
    def __init__(
        self,
        rect: pygame.Rect,
        source_rect: Optional[pygame.Rect]=None,
        parent_group: Optional['NestingGroup']=None,
        layer: int=0
    ) -> None:
        super().__init__()
        self.rect = rect
        self.source_rect = source_rect
        self.dirty = DirtyEnum.DIRTY
        self.visible = True
        self._layer = layer
        self.blendmode = 0
        self.source_rect = 0
        self._parent = parent_group
        if parent_group is not None:
            self.add(parent_group)

    @classmethod
    def from_sprite(cls, spr: pygame.sprite.Sprite) -> 'NesterSprite':
        '''
        Turns a regular `pygame.sprite.Sprite` into a `NesterSprite`. Copies as much as
        it can from the original `Sprite`, except for groups.
        '''
        # Make sure to take care of whichever attributes are
        # implemented in this variation of Sprite
        newspr = cls(
            getattr(spr, 'rect', pygame.Rect(0, 0, 0, 0)),
            source_rect=getattr(spr, 'source_rect', None),
            layer=spr.layer if hasattr(spr, 'layer') else 0
        )

        newspr.dirty = getattr(spr, 'dirty', newspr.dirty)
        newspr.visible = getattr(spr, 'visible', newspr.visible)
        newspr.blendmode = getattr(spr, 'blendmode', newspr.blendmode)
        newspr.image = getattr(spr, 'image', newspr.image)

        return newspr

    @property
    def visible(self) -> bool:
        '''
        If True, this `NesterSprite` will be visible. Set to False to hide this `NesterSprite`.
        '''
        return self._visible
    
    @visible.setter
    def visible(self, value: Union[bool, int]) -> None:
        self.visible = bool(value)
        if self.dirty == DirtyEnum.NOT_DIRTY:
            self.dirty == DirtyEnum.DIRTY

    @property
    def layer(self) -> int:
        '''
        Gets and sets the layer for this `NesterSprite`. Unlike regular `Sprite`s, you can set
        the layer after adding the `NesterSprite` to the `NestedGroup`. This works by calling
        `NestedGroup.change_layer()` with the `Sprite`'s parent group inside the setter.
        '''
        return self._layer
    
    @layer.setter
    def layer(self, value: int) -> None:
        if self.parent is not None:
            self.parent.change_layer(self, value)
        else:
            self._layer = value
    
    @property
    def parent(self) -> Optional['NestingGroup']:
        '''
        Gets and sets the parent `NestingGroup` of this `NesterSprite`.
        '''
        return self._parent
    
    @parent.setter
    def parent(self, nesting_group: Optional['NestingGroup']) -> None:
        if nesting_group is None:
            self.remove()
        else:
            self.add(nesting_group)
    
    def add(self, nesting_group: 'NestingGroup') -> None:
        '''
        Add the `NesterSprite` to a `NestingGroup`.

        Unlike normal `Sprite`s, `NestingSprite` can only be in one `NestingGroup`.
        '''
        if self in nesting_group:
            return
        self.remove_internal()
        self._parent = nesting_group
        nesting_group.add_internal(self)
        self.add_internal(nesting_group)

    def remove(self) -> 'NestingGroup':
        '''
        Remove the `NesterSprite` from its parent group and return it.
        Does not require a `group` argument because it can only be in one `NestingGroup`.
        Because of this, it is synonomous to `self.kill()`.
        '''
        return self.remove_internal()

    def kill(self) -> 'NestingGroup':
        '''
        Remove the `NesterSprite` from its parent group and return it.
        Synonomous to `self.remove()`.
        '''
        return self.remove_internal()

    def add_internal(self, nesting_group) -> None:
        '''
        # For internal use only!
        # Do not use unless you are going to subclass this class!
        This function is only documented for subclassers and main devs.

        ---

        This method adds the `NestingGroup` to the `NesterSprite`'s internal data.
        '''
        self.remove_internal()
        super().add_internal(nesting_group)
        self._parent = nesting_group

    def remove_internal(self) -> 'NestingGroup':
        '''
        # For internal use only!
        # Do not use unless you are going to subclass this class!
        This function is only documented for subclassers and main devs.

        ---

        This method removes the parent `NestingGroup` from the `NesterSprite`'s internal data
        and returns it.
        '''
        old_parent = self._parent
        super().remove(self._parent)
        self._parent = None
        return old_parent

    def __repr__(self) -> str:
        '''
        String Representation of `NesterSprite`
        '''
        if self.parent is None:
            return f'<{type(self).__name__} NesterSprite(unassigned)>'
        return f'<{type(self).__name__} NesterSprite(belongs to a {type(self.parent).__name__})>'

NestingGroupAddable = Union[NesterSprite, 'NestingGroup', Iterable['NestingGroupAddable']]

class NestingGroup(pygame.sprite.AbstractGroup):
    '''
    A group that nests. Update rect optimized. Supports layers.
    Does not remember a `NesterSprite`'s position within a layer.
    If it matters, use another `NestingGroup`.

    `layer` parameter refers to the default layer for adding sprites or groups
    to, while `parent_layer` refers to the position of the group itself in its parent.
    '''

    _init_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)

    def __init__(
        self,
        *sprites_or_groups: NestingGroupAddable,
        layer: Optional[int]=None,
        parent_group: Optional['NestingGroup']=None,
        parent_layer: int=0,
        **kwargs
    ) -> None:
        super().__init__()
        self._spr_layerdict: DefaultDict[int, List[NesterSprite]] = defaultdict(list)
        self._grp_layerdict: DefaultDict[int, List[NestingGroup]] = defaultdict(list)
        self._layerdict_full: Dict[int, List[Union[NesterSprite, 'NestingGroup']]] = {}
        self.groupdict: Dict[NestingGroup, int] = {}

        # Internal Cache Objects
        self._cache_sorted_sprites: Optional[List[NesterSprite]] = None
        self._cache_sorted_groups: Optional[List[NestingGroup]] = None
        self._cache_sorted_children: Optional[List[Union[NesterSprite, NestingGroup]]] = None

        # Adding type annotations
        self.spritedict: Dict[NesterSprite, pygame.Rect] = self.spritedict
        self.lostsprites: List[pygame.Rect] = self.lostsprites

        self._layer = parent_layer
        self.add(*sprites_or_groups, layer=layer, **kwargs)
        if parent_group is not None:
            parent_group.add(self)

    @property
    def parent(self) -> Optional['NestingGroup']:
        '''
        Gets and sets the parent `NestingGroup` of this group.
        '''
        return self._parent
    
    @parent.setter
    def parent(self, nesting_group: 'NestingGroup') -> None:
        nesting_group.add(self)
    
    @property
    def parent_layer(self) -> int:
        return self._layer
    
    @parent_layer.setter
    def parent_layer(self, layer: int) -> None:
        if self.parent is not None:
            self.parent.change_layer(self, layer)
        else:
            self._layer = layer

    def add(
        self,
        *sprites: NestingGroupAddable,
        layer: Optional[int]=None,
        **kwargs
    ) -> None:
        '''
        Adds `NesterSprite`s or other `NestingGroup`s to the `NestingGroup`. Can take
        plain `NesterSprite`s or iterables of them. `NestingGroup`s, however, will
        be nested. If you want to add the contents themselves, use `NestingGroup.sprites()`,
        `NestingGroup.groups()`, or `NestingGroup.children()`.

        This method raises `NestingRecursionError` if you attempt to add a parent group, direct
        or indirect, to this group.
        '''
        # the recursion detecting logic isn't here, it's in _add_group()
        for s in sprites:
            if isinstance(s, NesterSprite):
                if not self.has_internal(s):
                    self.add_internal(s, layer=layer)
                    s.add_internal(self)
            elif isinstance(s, NestingGroup):
                if not self._has_group(s):
                    self._add_group(s)
                    s._add_self_to_group(self)
            elif isinstance(s, Iterable):
                self.add(*s, layer=layer, **kwargs)
            else:
                warnings.warn(
                    'NestingGroup can only add NesterSprites or other NestingGroups',
                    TypeWarning,
                    stacklevel=2,
                )
        # Refresh the cache for the get_ordered_* methods
        self._cache_sorted_sprites = None
        self._cache_sorted_groups = None
        self._cache_sorted_children = None

    def remove(self, *sprites: NestingGroupAddable) -> None:
        '''
        Removes `NesterSprite`s or other `NestingGroup`s from this `NestingGroup`. Follows
        the same logic as `add()`.
        '''
        for s in sprites:
            if isinstance(s, NesterSprite):
                if self.has_internal(s):
                    self.remove_internal(s)
                    s.remove_internal(self)
            elif isinstance(s, NestingGroup):
                self._remove_group(s)
                s._remove_self_from_group(self)
            elif isinstance(s, Iterable):
                self.remove(*s)

    def _add_self_to_group(self, parent_group: 'NestingGroup'):
        '''
        # For internal use only!
        # Do not use unless you are going to subclass this class!
        This function is only documented for subclassers and main devs.

        ---

        Used by `NestingGroup` to add itself to other `NestingGroup`s internally.
        '''
        self._parent = parent_group
        self._propagate_dirty()

    def _add_group(self, nesting_group: 'NestingGroup', layer: Optional[int]=None):
        '''
        # For internal use only!
        # Do not use unless you are going to subclass this class!
        This function is only documented for subclassers and main devs.
        
        ---
        
        Used by `NestingGroup` to add other `NestingGroup`s to itself internally.
        '''
        # Yes, we combat recursive nesting with recursive methods. It should work...
        if nesting_group.has_recursive(self):
            raise NestingRecursionError('Group recursion is not allowed.')
        
        self.groupdict[nesting_group] = 0
        if layer is None:
            self._grp_layerdict[nesting_group.parent_layer].append(nesting_group)
        else:
            self._grp_layerdict[layer]

    def _propagate_dirty(self) -> None:
        '''
        # For internal use only!
        # Do not use unless you are going to subclass this class!
        This function is only documented for subclassers and main devs.
        
        ---
        
        Used by `NestingGroup` to indicate a redraw when added to another group.
        '''
        for s in self.spritedict:
            if s.dirty == DirtyEnum.NOT_DIRTY:
                s.dirty = DirtyEnum.DIRTY

        for g in self.groupdict:
            g._propagate_dirty()

    def _remove_self_from_group(self):
        '''
        # For internal use only!
        # Do not use unless you are going to subclass this class!
        This function is only documented for subclassers and main devs.

        ---

        Used by `NestingGroup` to remove itself from other `NestingGroup`s internally.
        '''
        self._parent = None
    
    def _remove_group(self, nesting_group: 'NestingGroup') -> None:
        '''
        # For internal use only!
        # Do not use unless you are going to subclass this class!
        This function is only documented for subclassers and main devs.

        ---

        Used by `NestingGroup` to remove other `NestingGroup`s from itself internally.
        '''
        del self.groupdict[nesting_group]

    def _has_group(self, nesting_group: 'NestingGroup') -> bool:
        '''
        # For internal use only!
        # Do not use unless you are going to subclass this class!
        This function is only documented for subclassers and main devs.

        ---

        Basically a version of `has_internal()` that tests for groups and not sprites.
        '''
        return nesting_group in self.groupdict

    def has_recursive(self, *sprites: NestingGroupAddable) -> bool:
        '''
        A recursive version of `has()` that checks child groups as well.
        '''
        if not sprites:
            return False

        for s in sprites:
            if isinstance(s, NesterSprite):
                if not (
                    self.has_internal(s) or
                    any(map(lambda g: g.has_recursive(s), self.groupdict))
                ):
                    return False
            elif isinstance(s, NestingGroup):
                if not (
                    self._has_group(s) or
                    any(map(lambda g: g.has_recursive(s), self.groupdict))
                ):
                    return False
            elif isinstance(s, Iterable):
                if not self.has_recursive(*s):
                    return False
        
        return True

    def add_internal(self, sprite: NesterSprite, layer: Optional[int]=None, **kwargs) -> None:
        '''
        # For internal use only!
        # Do not use unless you are going to subclass this class!
        This function is only documented for subclassers and main devs.
        
        ---
        
        Used by `NestingGroup` to add `NesterSprite`s internally.
        '''
        self.spritedict[sprite] = self._init_rect

        if sprite.dirty == DirtyEnum.NOT_DIRTY:
            sprite.dirty = DirtyEnum.DIRTY
        
        if layer is None:
            self._spr_layerdict[sprite.layer].append(sprite)
        else:
            self._spr_layerdict[layer].append(sprite)
            sprite._layer = layer

    def remove_internal(self, sprite: NesterSprite) -> None:
        '''
        # For internal use only!
        # Do not use unless you are going to subclass this class!
        This function is only documented for subclassers and main devs.
        
        ---
        
        Used by `NestingGroup` to remove NesterSprites internally.
        '''
        old_rect = self.spritedict[sprite]
        if old_rect is not self._init_rect:
            self.lostsprites.append(old_rect)
        self.lostsprites.append(sprite.rect)

        del self.spritedict[sprite]
        self._spr_layerdict[sprite.layer].remove(sprite)

        # layers are deleted when empty
        if not self._spr_layerdict[sprite.layer]:
            del self._spr_layerdict[sprite.layer]

    def get_sprites_from_layer(self, layer: int) -> List[NesterSprite]:
        '''
        Gets all the `NesterSprite`s in a certain layer.
        '''
        if layer not in self._spr_layerdict:
            return []
        return self._spr_layerdict[layer][:]

    def remove_sprites_of_layer(self, layer: int) -> List[NesterSprite]:
        '''
        Pops all the `NesterSprite`s in a certain layer and returns them.
        '''
        if layer not in self._spr_layerdict:
            return []
        sprites = self.get_sprites_from_layer(layer)
        self.remove(*sprites)
        return sprites

    def get_groups_from_layer(self, layer: int) -> List['NestingGroup']:
        '''
        Gets all child `NestingGroup`s in a certain layer.
        '''
        if layer not in self._grp_layerdict:
            return []
        return self._grp_layerdict[layer][:]

    def remove_groups_of_layer(self, layer: int) -> List['NestingGroup']:
        '''
        Pops all child `NestingGroup`s in a certain layer and returns them.
        '''
        if layer not in self._grp_layerdict:
            return []
        groups = self.get_groups_from_layer(layer)
        self.remove(*groups)
        return groups

    def get_children_from_layer(self, layer: int) -> List[Union[NesterSprite, 'NestingGroup']]:
        '''
        Gets all children in a certain layer.
        '''
        if layer not in self._layerdict_full:
            return []
        return self._layerdict_full[layer][:]
    
    def remove_children_of_layer(self, layer: int) -> List[Union[NesterSprite, 'NestingGroup']]:
        '''
        Pops all children in a certain layer and returns them.
        '''
        if layer not in self._layerdict_full:
            return []
        children = self.get_children_from_layer(layer)
        self.remove(*children)
        return children

    def change_layer(self, sprite: Union[NesterSprite, 'NestingGroup'], new_layer: int) -> None:
        '''
        Changes the layer of the given sprite or group to the new layer.
        '''
        self._layerdict_full[sprite._layer].remove(sprite)
        self._layerdict_full[new_layer].append(sprite)
        if isinstance(sprite, NesterSprite):
            self._spr_layerdict[sprite.layer].remove(sprite)
            self._spr_layerdict[new_layer].append(sprite)
        elif isinstance(sprite, NestingGroup):
            self._grp_layerdict[sprite.parent_layer].remove(sprite)
            self._grp_layerdict[new_layer].append(sprite)
        sprite._layer = new_layer

    def switch_layer(self, layer1: int, layer2: int) -> List[Union[NesterSprite, 'NestingGroup']]:
        '''
        Swaps sprites on given layers. Unlike LayeredUpdates, this is safe to call
        if any of the layers do not exist.

        Returns all `NesterSprite`s and `NestingGroup`s affected.
        '''
        out = []
        # basically just testing for abscence of both layers
        if all(k not in self._spr_layerdict for k in (layer1, layer2)):
            pass
        elif all(k in self._spr_layerdict for k in (layer1, layer2)): # both layers exist
            old_layer2_sprites = self.remove_sprites_of_layer(layer2)
            for s in self.get_sprites_from_layer(layer1):
                self.change_layer(s, layer2)
            self.add(*old_layer2_sprites, layer=layer1)
            out += old_layer2_sprites + self._spr_layerdict[layer2]
        elif layer1 in self._spr_layerdict:
            for s in self.get_sprites_from_layer(layer1):
                self.change_layer(s, layer2)
            out += self._spr_layerdict[layer2][:]
        elif layer2 in self._spr_layerdict:
            for s in self.remove_sprites_of_layer(layer2):
                self.change_layer(s, layer1)
            out += self._spr_layerdict[layer1][:]

        # now repeat with the group layerdict
        if all(k not in self._grp_layerdict for k in (layer1, layer2)):
            pass
        elif all(k in self._grp_layerdict for k in (layer1, layer2)): # both layers exist
            old_layer2_groups = self.remove_groups_of_layer(layer2)
            for s in self.get_groups_from_layer(layer1):
                self.change_layer(s, layer2)
            self.add(*old_layer2_groups, layer=layer1)
            out += old_layer2_groups + self._grp_layerdict[layer2]
        elif layer1 in self._grp_layerdict:
            for s in self.get_groups_from_layer(layer1):
                self.change_layer(s, layer2)
            out += self._grp_layerdict[layer2][:]
        elif layer2 in self._grp_layerdict:
            for s in self.remove_groups_of_layer(layer2):
                self.change_layer(s, layer1)
            out += self._grp_layerdict[layer1][:]

        return out

    def get_layerdict(self) -> Dict[int, List[Union[NesterSprite, 'NestingGroup']]]:
        '''
        Returns the internal mapping of integer layers to `NesterSprite`s and `NestingGroup`s.
        '''
        return dict(self._layerdict_full)

    def groups(self) -> List['NestingGroup']:
        '''
        Returns the child `NestingGroup`s of this `NestingGroup`.

        Note: While `Sprite.groups()` returns parent groups, this method returns groups contained
        in this group. For the parent group of this group, use `NestingGroup.parent`.
        '''
        return list(self.groupdict)

    def children(self) -> List[Union[NesterSprite, 'NestingGroup']]:
        '''
        Returns all child `NesterSprite`s and `NesterGroup`s of this `NestingGroup`.
        '''
        return list(self.spritedict) + list(self.groupdict)

    def sprites_ordered(self) -> List[NesterSprite]:
        '''
        Like `.sprites()` method, but sorts the sprites in ascending order by layer.
        '''
        if self._cache_sorted_sprites is None:
            self._cache_sorted_sprites = sorted(self.spritedict, key=lambda s: s.layer)
        return self._cache_sorted_sprites

    def groups_ordered(self) -> List['NestingGroup']:
        '''
        Like `.groups()` method, but sorts the groups in ascending order by layer.
        '''
        if self._cache_sorted_groups is None:
            self._cache_sorted_groups = sorted(self.groupdict, key=lambda g: g.parent_layer)
        return self._cache_sorted_groups

    def children_ordered(self) -> List[Union[NesterSprite, 'NestingGroup']]:
        '''
        '''
        if self._cache_sorted_children is None:
            self._cache_sorted_children = sorted(self._layerdict_full, key=lambda s: s._layer)
        return self._cache_sorted_children
