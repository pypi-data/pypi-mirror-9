========
Usage
========

PyInfoEpub can be used in two ways:


As Standalone
--------------
::

    $ python pyinfoepub.py -h
    $ python pyinfoepub.py <file.epub>
    
    
As a module
------------
::

    from pyinfoepub.infoepub import PyInfoEpub
    
    pyob = PyInfoEpub(<filename.epub>)
    extracted_info = pyob.get_info()
    print(extracted_info)
    
    # optional use a provided template in order to pretty display the information
    from pyinfoepub.templates.cli import TemplateCLI
    
    tob = TemplateCLI(extracted_info)
    tob.render()