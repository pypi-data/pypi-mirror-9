import os
import cap.plugin.toy.animal
import cap.plugin.toy.extra_animal
import matplotlib.pyplot as plt
from cap.model.som import SOM2D
from cap.settings import TYPE_TRAINING_SAMPLE
from cap.settings import TYPE_TEST_SAMPLE

ANIMAL_WEIGHT_STEP_SIZE = 0.2
ANIMAL_NBH_STEP_SIZE = 8
ANIMAL_MAX_NBH_SIZE = 5
ANIMAL_MAP_ROWS = 10
ANIMAL_MAP_COLS = 10
ANIMAL_RANDOM_SEED = None


def demo_toy_training():
    animals = cap.plugin.toy.animal.load_animals()
    test_samples = [cap.plugin.toy.extra_animal.load_animals(samples_type=TYPE_TEST_SAMPLE)[8]]
    features_size = len(animals[0].features)
    model = SOM2D(features_size,
                  max_nbh_size=9,
                  nbh_step_size=0.3,
                  map_rows=17,
                  map_cols=17,
                  )
    model.train(animals)
    model.load_visualize_samples(animals, test_samples)
    model.visualize_term()
    fig = plt.figure()
    ax = plt.subplot2grid((2, 3), (0, 0), colspan=2, rowspan=2)
    model.visualize_plt(ax,
                        29,
                        plt_style={0: 'r^',
                                   1: 'b*',
                                   },
                        )
    plt.tight_layout()
    plt.show()
