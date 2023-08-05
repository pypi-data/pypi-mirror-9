Import requirements::

    >>> import yafowil.loader
    >>> import yafowil.widget.dynatree
    >>> from yafowil.base import factory
    >>> from yafowil.utils import tag

A test tree::

    >>> tree = {'animal': ('Animals', { 
    ...             'mammal': ('Mammals', {
    ...                 'elephant': ('Elephant', None),
    ...                 'ape': ('Ape', None),
    ...                 'horse': ('Horse', None),
    ...             }), 
    ...             'bird': ('Birds', { 
    ...                 'duck': ('Duck', None),
    ...                 'swan': ('Swan', None),
    ...                 'turkey': ('Turkey', None),
    ...                 'hummingbird': ('Hummingbird', None),
    ...             }), 
    ...         })}

Test inline tree renderer separate::

    >>> from yafowil.widget.dynatree.widget import build_inline_dynatree
    >>> html = build_inline_dynatree(tree, 'animal', tag, ulid='dynatree-source')
    >>> print html
    <ul class="hiddenStructure" id="dynatree-source">
    <li class="selected" id="animal">Animals<ul>
    <li id="mammal">Mammals<ul>
    <li id="horse">Horse
    </li><li id="ape">Ape
    </li><li id="elephant">Elephant
    </li></ul>
    </li><li id="bird">Birds<ul>
    <li id="turkey">Turkey
    </li><li id="swan">Swan
    </li><li id="hummingbird">Hummingbird
    </li><li id="duck">Duck
    </li></ul>
    </li></ul>
    </li></ul>

Render plain widget, source is string::

    >>> widget = factory('dynatree', name='root', 
    ...                  props={'source': 'http://www.foo.bar/baz.json'})
    >>> pxml(widget())
    <div class="yafowil-widget-dynatree">
      <input id="input-root" name="root" type="hidden"/>
      <div class="dynatree-source hiddenStructure">http://www.foo.bar/baz.json</div>
      <div class="dynatree-params hiddenStructure">selectMode,1|minExpandLevel,1|rootVisible,False|autoCollapse,False|checkbox,True|imagePath,skin-bootstrap|type,remote</div>
      <div class="yafowil-widget-dynatree-tree"/>
    </div>
    <BLANKLINE>

Render plain widget, source is tree::

    >>> widget = factory('dynatree', name='root', 
    ...                  props={'source': tree})
    >>> pxml(widget())
    <div class="yafowil-widget-dynatree">
      <input id="input-root" name="root" type="hidden"/>
      <ul class="hiddenStructure" id="dynatree-source-root">
    <li id="animal">Animals<ul>
    <li id="mammal">Mammals<ul>
    <li id="horse">Horse
    </li><li id="ape">Ape
    </li><li id="elephant">Elephant
    </li></ul>
    </li><li id="bird">Birds<ul>
    <li id="turkey">Turkey
    </li><li id="swan">Swan
    </li><li id="hummingbird">Hummingbird
    </li><li id="duck">Duck
    </li></ul>
    </li></ul>
    </li></ul>
      <div class="dynatree-params hiddenStructure">selectMode,1|minExpandLevel,1|rootVisible,False|autoCollapse,False|checkbox,True|imagePath,skin-bootstrap|type,local|initId,dynatree-source-root</div>
      <div class="yafowil-widget-dynatree-tree"/>
    </div>
    <BLANKLINE>

Render plain widget, source is callable::

    >>> def tree_callable(widget, data):
    ...     return tree
    
    >>> widget = factory('dynatree', name='root', 
    ...                  props={'source': tree_callable})
    >>> pxml(widget())
    <div class="yafowil-widget-dynatree">
      <input id="input-root" name="root" type="hidden"/>
      <ul class="hiddenStructure" id="dynatree-source-root">
    <li id="animal">Animals<ul>
    <li id="mammal">Mammals<ul>
    <li id="horse">Horse
    </li><li id="ape">Ape
    </li><li id="elephant">Elephant
    </li></ul>
    </li><li id="bird">Birds<ul>
    <li id="turkey">Turkey
    </li><li id="swan">Swan
    </li><li id="hummingbird">Hummingbird
    </li><li id="duck">Duck
    </li></ul>
    </li></ul>
    </li></ul>
      <div class="dynatree-params hiddenStructure">selectMode,1|minExpandLevel,1|rootVisible,False|autoCollapse,False|checkbox,True|imagePath,skin-bootstrap|type,local|initId,dynatree-source-root</div>
      <div class="yafowil-widget-dynatree-tree"/>
    </div>
    <BLANKLINE>

Try to render plain widget, source is invalid::

    >>> widget = factory('dynatree', name='root', 
    ...                  value='ape',
    ...                  props={'source': object()})
    >>> pxml(widget())
    Traceback (most recent call last):
      ...
    ValueError: resulting source must be [o]dict or string

Render plain widget, source is tree, preselect ape, single select::

    >>> widget = factory('dynatree', name='root', 
    ...                  value='ape',
    ...                  props={'source': tree})
    >>> pxml(widget())
    <div class="yafowil-widget-dynatree">
      <input id="input-root" name="root" type="hidden" value="ape"/>
      <ul class="hiddenStructure" id="dynatree-source-root">
    <li id="animal">Animals<ul>
    <li id="mammal">Mammals<ul>
    <li id="horse">Horse
    </li><li class="selected" id="ape">Ape
    </li><li id="elephant">Elephant
    </li></ul>
    </li><li id="bird">Birds<ul>
    <li id="turkey">Turkey
    </li><li id="swan">Swan
    </li><li id="hummingbird">Hummingbird
    </li><li id="duck">Duck
    </li></ul>
    </li></ul>
    </li></ul>
      <div class="dynatree-params hiddenStructure">selectMode,1|minExpandLevel,1|rootVisible,False|autoCollapse,False|checkbox,True|imagePath,skin-bootstrap|type,local|initId,dynatree-source-root</div>
      <div class="yafowil-widget-dynatree-tree"/>
    </div>
    <BLANKLINE>

Render plain widget, source is tree, preselect ape and swan, multi select::

    >>> widget = factory('dynatree', name='root', 
    ...                  value=['ape', 'swan'],
    ...                  props={'source': tree, 'selectMode': 1})
    >>> pxml(widget())
    <div class="yafowil-widget-dynatree">
      <input id="input-root" name="root" type="hidden" value="ape|swan"/>
      <ul class="hiddenStructure" id="dynatree-source-root">
    <li id="animal">Animals<ul>
    <li id="mammal">Mammals<ul>
    <li id="horse">Horse
    </li><li class="selected" id="ape">Ape
    </li><li id="elephant">Elephant
    </li></ul>
    </li><li id="bird">Birds<ul>
    <li id="turkey">Turkey
    </li><li class="selected" id="swan">Swan
    </li><li id="hummingbird">Hummingbird
    </li><li id="duck">Duck
    </li></ul>
    </li></ul>
    </li></ul>
      <div class="dynatree-params hiddenStructure">selectMode,1|minExpandLevel,1|rootVisible,False|autoCollapse,False|checkbox,True|imagePath,skin-bootstrap|type,local|initId,dynatree-source-root</div>
      <div class="yafowil-widget-dynatree-tree"/>
    </div>
    <BLANKLINE>
        
Extract from selectMode=1 - means single selection::

    >>> widget = factory('dynatree', name='root', 
    ...                  props={'source': tree, 'selectMode': 1})
    >>> data = widget.extract({'root': 'somevalue|'})
    >>> data
    <RuntimeData root, value=<UNSET>, extracted='somevalue' at ...>
    
Extract from selectMode=2 - means multi selection::

    >>> widget = factory('dynatree', name='root', 
    ...                  props={'source': tree, 'selectMode': 2})
    >>> data = widget.extract({'root': 'somevalue|'})
    >>> data
    <RuntimeData root, value=<UNSET>, extracted=['somevalue'] at ...>         

    >>> data = widget.extract({'root': 'somevalue|othervalue'})
    >>> data
    <RuntimeData root, value=<UNSET>, extracted=['somevalue', 'othervalue'] at ...>

Extract empty::

    >>> data = widget.extract({})
    >>> data.printtree()
    <RuntimeData root, value=<UNSET>, extracted=<UNSET> at ...>
