__author__ = 'Georgios Rizos (georgerizos@iti.gr)'

from reveal_user_annotation.common.config_package import get_raw_datasets_path, get_memory_path
from reveal_user_classification.datautil.asu_read_data import read_adjacency_matrix
from reveal_user_classification.eps_randomwalk.benchmarks.benchmark_design import similarity_slice_benchmark


########################################################################################################################
# Configure experiment.
########################################################################################################################
# Select dataset
DATASET = "YouTube"  # Choices are: BlogCatalog, Flickr, YouTube.

# Define approximate PageRank method parameters.
ALPHA = 0.6
EPSILON = 0.00001

# Define laziness factor for the lazy PageRank.
LAZINESS = 0.5

NUMBER_OF_TRIALS = 1

########################################################################################################################
# Read data.
########################################################################################################################
# Define data path.
EDGE_LIST_PATH = get_raw_datasets_path() + "/ASU/" + DATASET + "/edges.csv"
adjacency_matrix = read_adjacency_matrix(EDGE_LIST_PATH, ',')
number_of_nodes = adjacency_matrix.shape[0]

profile_stat_folder = get_memory_path() + "/ASU/" + DATASET + "/profile/individual"

########################################################################################################################
# Perform experiment.
########################################################################################################################
profiler_stats = similarity_slice_benchmark(NUMBER_OF_TRIALS,
                                            adjacency_matrix,
                                            ALPHA,
                                            EPSILON,
                                            LAZINESS,
                                            profile_stat_folder)
