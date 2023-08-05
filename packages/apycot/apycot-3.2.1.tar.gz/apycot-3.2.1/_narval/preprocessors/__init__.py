# make it work in 'dev' mode: look for preprocessors in known cubes

try:
    import narvalbot
except:
    from cubes.narval import narvalbot
    import sys
    sys.modules['narvalbot'] = narvalbot

if narvalbot.MODE == 'dev':
    # we are running from sources, cubicweb *should* be available,
    # let's use it as starting point to look for cubes in which there
    # is a _narval directory
    import os, os.path as osp
    from cubicweb import CW_SOFTWARE_ROOT
    cubesdir = osp.join(CW_SOFTWARE_ROOT, '..', 'cubes')
    for cube in os.listdir(cubesdir):
        pluginsdir = osp.abspath(osp.join(cubesdir, cube, '_narval', 'preprocessors'))
        if osp.isdir(pluginsdir):
            __path__.append(pluginsdir)
