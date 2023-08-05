import os

"""

This module is all about constant value that are used in this application

"""

# > > > > > > > > > > > > > random values < < < < < < < < < <
DFLT_SEED = None
DEMO_SEED = 20
TEST_SEED = DEMO_SEED

# > > > > > > > > > > > > > development files & folders < < < < < < < < < <
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

OUT_DIR = '/home/jessada/development/projects/COMPAS/out/'
FIGS_TMP_OUT_DIR = os.path.join(OUT_DIR, 'figs_tmp')
TERM_TMP_OUT_DIR = os.path.join(OUT_DIR, 'term_tmp')

# > > > > > > > > > > > > > model parameters < < < < < < < < < <
DFLT_MAP_SIZE = 100
DFLT_WEIGHT_STEP_SIZE = 0.2
DFLT_NBH_STEP_SIZE = 1
DFLT_MAX_NBH_SIZE = 10
DFLT_MAP_ROWS = 17
DFLT_MAP_COLS = 17

# > > > > > > > > > > > > > samples type < < < < < < < < < <
TYPE_TRAINING_SAMPLE = 'training'
TYPE_TEST_SAMPLE = 'test'
