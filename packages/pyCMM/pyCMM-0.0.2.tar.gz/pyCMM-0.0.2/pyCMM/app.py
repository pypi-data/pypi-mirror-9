import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import datetime
from math import ceil
from cap.model.som import SOM2D
from cap.settings import DFLT_WEIGHT_STEP_SIZE
from cap.settings import DFLT_NBH_STEP_SIZE
from cap.settings import DFLT_MAX_NBH_SIZE
from cap.settings import DFLT_MAP_ROWS
from cap.settings import DFLT_MAP_COLS
from cap.settings import DFLT_SEED
from cap.settings import FIGS_TMP_OUT_DIR
from cap.settings import TERM_TMP_OUT_DIR
from cap.settings import TYPE_TRAINING_SAMPLE
from cap.settings import TYPE_TEST_SAMPLE
from cap.plugin.base import load_samples


ROOT_DEMO_DATA = '/home/jessada/development/projects/COMPAS/cap/data/'
DEMO_TRAINING_FEATURES = os.path.join(ROOT_DEMO_DATA,
                                      'demo_training_features.txt')
DEMO_TRAINING_CLASSES = os.path.join(ROOT_DEMO_DATA,
                                     'demo_training_classes.txt')
DEMO_TEST_FEATURES = os.path.join(ROOT_DEMO_DATA,
                                  'demo_test_features.txt')
DEMO_TEST_CLASSES = os.path.join(ROOT_DEMO_DATA,
                                 'demo_test_classes.txt')
DEMO_OUT_DIR = '/home/jessada/development/projects/COMPAS/out/tmp/'
PARADIGM_WEIGHT_STEP_SIZE = 0.2
PARADIGM_NBH_STEP_SIZE = 0.36
PARADIGM_MAX_NBH_SIZE = 15
PARADIGM_MAP_ROWS = 20
PARADIGM_MAP_COLS = 20
PARADIGM_RANDOM_SEED = None

TEST_DATA_PROP = 'test data'

def get_time_stamp():
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

#running demo version of SOM2D using Paradigm data
def demo_som2d_paradigm():
    visualize_params = []
    visualize_params.append({'type': 'terminal',
                             'txt_width': 15,
                             })
    visualize_params.append({'type': 'scatter',
                             'prop_name': 'MSI_status',
                             'plt_style': {'MSI-H': 'r^',
                                           'MSI-L': 'b*',
                                           'MSS': 'mo',
                                           TEST_DATA_PROP: 'k+',
                                           },
                             })
    visualize_params.append({'type': 'scatter',
                             'prop_name': 'methylation_subtype',
                             'plt_style': {'CIMP.H': 'r^',
                                           'CIMP.L': 'b*',
                                           'Cluster3': 'gv',
                                           'Cluster4': 'mo',
                                           TEST_DATA_PROP: 'k+',
                                           },
                             })
#    visualize_params.append({'type': 'contour',
#                             'prop_name': 'days_to_last_known_alive',
#                             'min_cutoff': 400,
#                             'max_cutoff': 720,
#                             })
#    visualize_params.append({'type': 'debugging contour filter',
#                             'prop_name': 'days_to_last_known_alive',
#                             'min_cutoff': 400,
#                             'max_cutoff': 720,
#                             })
#    visualize_params.append({'type': 'debugging contour text',
#                             'prop_name': 'days_to_last_known_alive',
#                             })
    visualize_params.append({'type': 'scatter',
                             'prop_name': 'tumor_stage',
                             'plt_style': {'Stage I': 'r^',
                                           'Stage IIA': 'b*',
                                           'Stage IIB': 'yD',
                                           'Stage IIIA': 'mH',
                                           'Stage IIIB': 'co',
                                           'Stage IIIC': 'gv',
                                           'Stage IV': 'mx',
                                           },
                             })
    visualize_params.append({'type': 'scatter',
                             'prop_name': 'anatomic_organ_subdivision',
                             'plt_style': {'Ascending Colon': 'r^',
                                           'Cecum': 'b*',
                                           'Descending Colon': 'yD',
                                           'Hepatic Flexure': 'mH',
                                           'Rectosigmoid Junction': 'co',
                                           'Rectum': 'gv',
                                           'Sigmoid Colon': 'mx',
                                           'Transverse Colon': 'bp',
                                           },
                             })
    visualize_params.append({'type': 'scatter',
                             'prop_name': 'tumor_site',
                             'plt_style': {'1 - right colon': 'r^',
                                           '2 - transverse colon': 'b*',
                                           '3 - left colon': 'mo',
                                           '4 - rectum': 'gv',
                                           },
                             })
    out = som2d_paradigm(DEMO_TRAINING_FEATURES,
                         DEMO_TRAINING_CLASSES,
                         test_features_file=DEMO_TEST_FEATURES,
                         visualize_params=visualize_params,
                         )
    return out

#A wrapped layer to call som2d using Paradigm configuration
def som2d_paradigm(training_features_file,
                   training_classes_file,
                   test_features_file=None,
                   visualize_params=[],
                   ):
    current_time = get_time_stamp()
    out_folder = os.path.join(DEMO_OUT_DIR,
                              'Paradigm/'+current_time)
    if not os.path.isdir(out_folder):
        os.makedirs(out_folder)
    training_samples = load_samples(training_features_file,
                                    training_classes_file)
    if test_features_file is not None:
        test_samples = load_samples(test_features_file,
                                    samples_type=TYPE_TEST_SAMPLE)
    else:
        test_samples = None
    #shorten training samples name
    for training_sample in training_samples:
        training_sample.name = training_sample.name.replace("TCGA-", "")
    #setup test samples classes
    for test_sample in test_samples:
        for prop_name in training_samples[0].classes:
            test_sample.classes[prop_name] = TEST_DATA_PROP
    #call SOM2D
    return som2d(training_samples,
                 test_samples,
                 visualize_params=visualize_params,
                 out_folder=out_folder,
                 map_rows=PARADIGM_MAP_ROWS,
                 map_cols=PARADIGM_MAP_COLS,
                 weight_step_size=PARADIGM_WEIGHT_STEP_SIZE,
                 nbh_step_size=PARADIGM_NBH_STEP_SIZE,
                 max_nbh_size=PARADIGM_MAX_NBH_SIZE,
                 random_seed=PARADIGM_RANDOM_SEED,
                 )

#wrap all require stuffs to run SOM2D
def som2d(training_samples,
          test_samples=[],
          visualize_params=[],
          out_folder=None,
          map_rows=DFLT_MAP_ROWS,
          map_cols=DFLT_MAP_COLS,
          weight_step_size=DFLT_WEIGHT_STEP_SIZE,
          nbh_step_size=DFLT_NBH_STEP_SIZE,
          max_nbh_size=DFLT_MAX_NBH_SIZE,
          random_seed=DFLT_SEED,
          ):
    features_size = len(training_samples[0].features)
    model = SOM2D(features_size,
                  map_rows=map_rows,
                  map_cols=map_cols,
                  weight_step_size=weight_step_size,
                  nbh_step_size=nbh_step_size,
                  max_nbh_size=max_nbh_size,
                  random_seed=random_seed,
                  )
    #train and load sample for visualize
    model.train(training_samples)
    visualize_samples = []
    for sample in training_samples:
        visualize_samples.append(sample)
    for sample in test_samples:
        visualize_samples.append(sample)
    model.load_visualize_samples(visualize_samples)
    pdf_font = {'family' : 'monospace',
                'size'   : 3}
    matplotlib.rc('font', **pdf_font)
    #prepare text to visualize training attributes
    training_samples_size = len(training_samples)
    test_samples_size = len(test_samples)
    iterations = int(ceil(float(model.max_nbh_size)/model.nbh_step_size))
    col1_txt_fmt = "{caption:<28}:{value:>7}"
    col1_txt = []
    col1_txt.append(col1_txt_fmt.format(caption="number of training samples",
                                        value=training_samples_size))
    col1_txt.append(col1_txt_fmt.format(caption="number of test samples",
                                        value=test_samples_size))
    col1_txt.append(col1_txt_fmt.format(caption="features size",
                                        value=model.features_size))
    col1_txt.append(col1_txt_fmt.format(caption="training iterations",
                                        value=iterations))
    col2_txt_fmt = "{caption:<24}:{value:>12}"
    col2_txt = []
    col2_txt.append(col2_txt_fmt.format(caption="map rows",
                                        value=model.map_rows))
    col2_txt.append(col2_txt_fmt.format(caption="map cols",
                                        value=model.map_cols))
    col2_txt.append(col2_txt_fmt.format(caption="max neighborhod size",
                                        value=model.max_nbh_size))
    col2_txt.append(col2_txt_fmt.format(caption="neighborhood step size",
                                        value=model.nbh_step_size))
    col2_txt.append(col2_txt_fmt.format(caption="random seed",
                                        value=model.random_seed))

    #generate individual reports
    fig_rows = 1
    fig_cols = 1
    legend_width = 1
    description_height = 1
    fig_width = 4
    fig_height = 4
    plt_rows = fig_rows*fig_height + description_height
    plt_cols = (fig_width+legend_width) * fig_cols
    plt_txt_size = int(ceil(12/fig_rows))
    desc_txt_size = 10 - fig_rows
    fig = plt.figure()
    eps_file_names = []
    idx = 0
    for params in visualize_params:
        fig_col = (idx%fig_cols) * (fig_width+legend_width)
        fig_row = ((idx//fig_cols)*fig_height) + description_height
        plt.subplot2grid((1, 1), (0, 0))
        ax = plt.subplot2grid((plt_rows, plt_cols),
                              (fig_row, fig_col),
                              colspan=fig_width,
                              rowspan=fig_height,
                              )
        if params['type'] == 'terminal':
            out_file = os.path.join(out_folder,
                                    'terminal_out.txt')
            out_term = model.visualize_term(txt_width=params['txt_width'],
                                            out_file=out_file,
                                            )
            model.visualize_sample_name(ax, txt_size=plt_txt_size)
            eps_file_name = os.path.join(out_folder,
                                         'sample_names.eps')
        elif params['type'] == 'scatter':
            prop_name = params['prop_name']
            model.visualize_plt(ax,
                                prop_name,
                                params['plt_style'],
                                txt_size=plt_txt_size,
                                )
            eps_file_name = os.path.join(out_folder,
                                         'scatter_'+prop_name+'.eps')
        elif params['type'] == 'debugging contour text':
            prop_name = params['prop_name']
            model.debugging_contour_txt(ax,
                                        prop_name,
                                        txt_size=plt_txt_size,
                                        )
            eps_file_name = os.path.join(out_folder,
                                         'dbg_contour_'+prop_name+'.eps')
        elif params['type'] == 'debugging contour filter':
            prop_name = params['prop_name']
            model.debugging_contour_filter(ax,
                                           prop_name,
                                           min_cutoff=params['min_cutoff'],
                                           max_cutoff=params['max_cutoff'],
                                           txt_size=plt_txt_size,
                                           )
            eps_file_name = os.path.join(out_folder,
                                         'dbg_contour_filter_'+prop_name+'.eps')
        elif params['type'] == 'contour':
            prop_name = params['prop_name']
            out_plt = model.visualize_contour(ax,
                                              prop_name,
                                              min_cutoff=params['min_cutoff'],
                                              max_cutoff=params['max_cutoff'],
                                              txt_size=plt_txt_size,
                                              )
            cbaxes = plt.subplot2grid((plt_rows, plt_cols*2),
                                      (fig_row, (fig_col+2)*2),
                                      rowspan=fig_height,
                                      )
            plt.colorbar(out_plt, cax=cbaxes)
            eps_file_name = os.path.join(out_folder,
                                         'contour_'+prop_name+'.eps')
        else:
            continue
        ax = plt.subplot2grid((plt_rows, plt_cols),
                              (0, 0),
                              colspan=fig_cols*(fig_width+legend_width))
        model.visualize_txt(ax, col1_txt, col2_txt, txt_size=desc_txt_size)
        fig.savefig(eps_file_name, bbox_inches='tight', pad_inches=0.1)
        eps_file_names.append(eps_file_name)

    #generate summary pdf report
    fig_rows = 2
    fig_cols = 3
    legend_width = 1
    description_height = 1
    fig_width = 2
    fig_height = 2
    plt_rows = fig_rows*fig_height + description_height
    plt_cols = (fig_width+legend_width) * fig_cols
    plt_txt_size = int(ceil(12/fig_rows))
    desc_txt_size = 12 - fig_rows
    fig = plt.figure()
    idx = 0
    #plot figures
    for params in visualize_params:
        fig_col = (idx%fig_cols) * (fig_width+legend_width)
        fig_row = ((idx//fig_cols)*fig_height) + description_height
        ax = plt.subplot2grid((plt_rows, plt_cols),
                              (fig_row, fig_col),
                              colspan=fig_width,
                              rowspan=fig_height,
                              )
        if params['type'] == 'terminal':
            out_file = os.path.join(out_folder,
                                    'terminal_out.txt')
            out_term = model.visualize_term(txt_width=params['txt_width'],
                                            out_file=out_file,
                                            )
            model.visualize_sample_name(ax, txt_size=plt_txt_size)
        elif params['type'] == 'scatter':
            out_plt = model.visualize_plt(ax,
                                          params['prop_name'],
                                          params['plt_style'],
                                          txt_size=plt_txt_size,
                                          )
        elif params['type'] == 'debugging contour filter':
            out_plt = model.debugging_contour_filter(ax,
                                                     params['prop_name'],
                                                     min_cutoff=params['min_cutoff'],
                                                     max_cutoff=params['max_cutoff'],
                                                     txt_size=plt_txt_size,
                                                     )
        elif params['type'] == 'contour':
            out_plt = model.visualize_contour(ax,
                                              params['prop_name'],
                                              min_cutoff=params['min_cutoff'],
                                              max_cutoff=params['max_cutoff'],
                                              txt_size=plt_txt_size,
                                              )
            cbaxes = plt.subplot2grid((plt_rows, plt_cols*2),
                                      (fig_row, (fig_col+2)*2),
                                      rowspan=fig_height,
                                      )
            plt.colorbar(out_plt, cax=cbaxes)
        elif params['type'] == 'debugging contour text':
            out_plt = model.debugging_contour_txt(ax,
                                                  params['prop_name'],
                                                  txt_size=plt_txt_size,
                                                  )
        idx += 1
    ax = plt.subplot2grid((plt_rows, plt_cols),
                          (0, 0),
                          colspan=fig_cols*(fig_width+legend_width))
    out_plt = model.visualize_txt(ax, col1_txt, col2_txt, txt_size=desc_txt_size)
    plt.tight_layout()
    summary_pdf_file_name = os.path.join(out_folder, 'summary.pdf')
    fig.savefig(summary_pdf_file_name, bbox_inches='tight', pad_inches=0.1)
    return {"summary file": summary_pdf_file_name,
            "eps reports": eps_file_names,
            "terminal file": out_term,
            }
