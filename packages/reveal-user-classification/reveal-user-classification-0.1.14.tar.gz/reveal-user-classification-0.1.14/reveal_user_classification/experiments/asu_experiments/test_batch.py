__author__ = 'Georgios Rizos (georgerizos@iti.gr)'

import os
import time
import numpy as np
from scipy.sparse import issparse
from sklearn.multiclass import OneVsRestClassifier
from sklearn import svm
from itertools import product
from operator import getitem
import statistics

from reveal_user_annotation.common.config_package import get_threads_number, get_raw_datasets_path, get_memory_path
from reveal_user_annotation.common.datarw import get_file_row_generator
from reveal_user_classification.datautil.asu_read_data import read_adjacency_matrix, read_node_label_matrix
from reveal_user_classification.datautil.feature_rw_util import write_features, read_features
from reveal_user_classification.datautil.prediction_rw_util import write_predictions, read_predictions
from reveal_user_classification.experiments import evaluation
from reveal_user_classification.experiments.evaluation import form_node_label_prediction_matrix
from reveal_user_classification.embedding.arcte.arcte import arcte
from reveal_user_classification.embedding.competing_methods import mroc, base_communities, louvain, replicator_eigenmaps, laplacian_eigenmaps
from reveal_user_classification.embedding.common import normalize_community_features
from reveal_user_classification.experiments.holdout import generate_folds, get_folds_generator
from reveal_user_classification.embedding.community_weighting import community_weighting


def store_performace_measures(performance_measures, memory_path, experiment_string):
    # Unpack performance measures
    mean_macro_precision = performance_measures[0]
    mean_micro_precision = performance_measures[1]
    mean_macro_recall = performance_measures[2]
    mean_micro_recall = performance_measures[3]
    mean_macro_F1 = performance_measures[4]
    mean_micro_F1 = performance_measures[5]
    F1 = performance_measures[6]

    number_of_categories = F1.shape[1]

    # Store average scores
    path = memory_path + "/scores/" + experiment_string + "_average_scores.txt"
    if not os.path.exists(path):
        with open(path, "w") as fp:
            write_average_score_row(fp, "Macro Precision", mean_macro_precision)
            fp.write("\n\n")

            write_average_score_row(fp, "Micro Precision", mean_micro_precision)
            fp.write("\n\n")

            write_average_score_row(fp, "Macro Recall", mean_macro_recall)
            fp.write("\n\n")

            write_average_score_row(fp, "Micro Recall", mean_micro_recall)
            fp.write("\n\n")

            write_average_score_row(fp, "Macro F1", mean_macro_F1)
            fp.write("\n\n")

            write_average_score_row(fp, "Micro F1", mean_micro_F1)

    # Store category-specific F scores
    path = memory_path + "/scores/" + experiment_string + "_F_scores.txt"
    if not os.path.exists(path):
        with open(path, "w") as fp:
            for c in np.arange(number_of_categories):
                row = list(F1[:, c])
                row = [str(score) for score in row]
                row = "\t".join(row) + "\n"
                fp.write(row)


def write_average_score_row(fp, score_name, scores):
    """
    Simple utility function that writes an average score row in a file designated by a file pointer.

    Inputs:  - fp: A file pointer.
             - score_name: What it says on the tin.
             - scores: An array of average score values corresponding to each of the training set percentages.
    """
    row = "--" + score_name + "--" + "\n"
    fp.write(row)
    row = list(scores)
    row = [str(score) for score in row]
    row = "\t".join(row)
    fp.write(row)


def extract_features(adjacency_matrix, dataset, method_name, feature_extraction_params):
    method_string = method_name.lower()

    if feature_extraction_params is not None:
        for param, value in feature_extraction_params:
            method_string += "_" + param + str(value)

    feature_path = get_memory_path() + "/ASU/" + dataset + "/features/" + method_string + "_features"
    time_path = get_memory_path() + "/ASU/" + dataset + "/features/" + method_string + "_time.txt"
    if not (os.path.exists(feature_path + ".pkl") or os.path.exists(feature_path + ".npy")):
        implemented_methods = set()
        implemented_methods.update(["arcte",
                                    "mroc",
                                    "louvain",
                                    "lapeig",
                                    "egocomm",
                                    "repeig"])

        # Calculate and time feature extraction
        method_name_lowercase = method_name.lower()
        start_time = time.time()
        if method_name_lowercase in implemented_methods:
            if method_name_lowercase == "arcte":
                rho = feature_extraction_params[0][1]
                eps = feature_extraction_params[1][1]

                features = arcte(adjacency_matrix, rho, eps)
            elif method_name_lowercase == "mroc":
                features = mroc(adjacency_matrix, 1000)
            elif method_name_lowercase == "louvain":
                features = louvain(adjacency_matrix)
            elif method_name_lowercase == "lapeig":
                dim = feature_extraction_params[0][1]
                features = laplacian_eigenmaps(adjacency_matrix, dim)
            elif method_name_lowercase == "egocomm":
                features = base_communities(adjacency_matrix)
            elif method_name_lowercase == "repeig":
                dim = feature_extraction_params[0][1]
                features = replicator_eigenmaps(adjacency_matrix, dim)
            else:
                print("No implementation.")
                raise NotImplementedError
        else:
            print("Cannot find features or implementation.")
            raise NotImplementedError
        elapsed_time = time.time() - start_time

        # Store features and time
        write_features(feature_path, features)
        with open(time_path, "w") as fp:
            row = str(elapsed_time)
            fp.write(row)
    else:
        # Read features and feature extraction time
        features = read_features(method_name, feature_path)
        file_row_gen = get_file_row_generator(time_path, "\t")
        elapsed_time = float(next(file_row_gen)[0])

    return features, elapsed_time, method_string


def run_asu_experiment(dataset, percentages, methods, trial_num, feature_extraction_params, classifier_params):
    """
    Runs a batch of experiment on an ASU dataset.
    """
    # Read graphs
    EDGE_LIST_PATH = get_raw_datasets_path() + "/ASU/" + dataset + "/edges.csv"
    adjacency_matrix = read_adjacency_matrix(EDGE_LIST_PATH, ',')
    number_of_nodes = adjacency_matrix.shape[0]

    # Read labels
    NODE_LABEL_LIST_PATH = get_raw_datasets_path() + "/ASU/" + dataset + "/group-edges.csv"
    node_label_matrix, number_of_categories, labelled_node_indices = read_node_label_matrix(NODE_LABEL_LIST_PATH, ',', number_of_nodes)

    # Start batch
    for method_name in methods:
        # For all various parameters.
        method_parameters = feature_extraction_params[method_name]

        number_of_method_parameters = len(method_parameters)
        parameter_names = list()
        for m_p in range(number_of_method_parameters):
            parameter_names.append(method_parameters[m_p][0])

        if number_of_method_parameters > 0:
            parameter_product = product(*[getitem(parameters, 1) for parameters in method_parameters])
        else:
            parameter_product = [None, ]

        for parameter_instance in parameter_product:
            if parameter_instance is None:
                method_input = None
            else:
                method_input = list(zip(parameter_names,
                                        parameter_instance))

            # Read or generate features + time
            features, feature_extraction_time, method_string = extract_features(adjacency_matrix,
                                                                                dataset,
                                                                                method_name,
                                                                                method_input)

            if issparse(features):
                features = normalize_community_features(features)

            # For all various classifier parameters.
            model_parameters = classifier_params[method_name]

            number_of_model_parameters = len(model_parameters)
            classification_parameter_names = list()
            for model_p in range(number_of_model_parameters):
                classification_parameter_names.append(model_parameters[model_p][0])

            model_parameter_product = product(*[getitem(parameters, 1) for parameters in model_parameters])

            # Form classifier string.
            for model_parameter_instance in model_parameter_product:
                print(method_name, parameter_instance, model_parameter_instance)
                c = model_parameter_instance[0]
                fit_intercept = model_parameter_instance[1]
                classifier_string = "C" + str(c) + "_" + "intercept" + str(fit_intercept) + "_"

                # Generate 30 training folds out of the training part that remains and store seed folds
                mean_macro_precision = np.zeros(percentages.size, dtype=np.float)
                mean_micro_precision = np.zeros(percentages.size, dtype=np.float)
                mean_macro_recall = np.zeros(percentages.size, dtype=np.float)
                mean_micro_recall = np.zeros(percentages.size, dtype=np.float)
                mean_macro_F1 = np.zeros(percentages.size, dtype=np.float)
                mean_micro_F1 = np.zeros(percentages.size, dtype=np.float)
                F1 = np.zeros((percentages.size, number_of_categories), dtype=np.float)
                for p in np.arange(percentages.size):
                    percentage = percentages[p]
                    # Initialize the metric storage arrays to zero
                    macro_precision = np.zeros(trial_num, dtype=np.float)
                    micro_precision = np.zeros(trial_num, dtype=np.float)
                    macro_recall = np.zeros(trial_num, dtype=np.float)
                    micro_recall = np.zeros(trial_num, dtype=np.float)
                    macro_F1 = np.zeros(trial_num, dtype=np.float)
                    micro_F1 = np.zeros(trial_num, dtype=np.float)
                    trial_F1 = np.zeros((trial_num, number_of_categories), dtype=np.float)

                    dataset_memory_folder = get_memory_path() + "/ASU/" + dataset
                    folds = get_folds_generator(node_label_matrix,
                                                labelled_node_indices,
                                                number_of_categories,
                                                dataset_memory_folder,
                                                percentage,
                                                trial_num)
                    hypothesis_training_times = list()
                    prediction_times = list()
                    for trial in np.arange(trial_num):
                        train, test = next(folds)
                        ########################################################################################################
                        # Separate train and test sets
                        ########################################################################################################
                        X_train, X_test, y_train, y_test = features[train, :],\
                                                           features[test, :],\
                                                           node_label_matrix[train, :],\
                                                           node_label_matrix[test, :]

                        # X_train, X_test, feature_filtering_time, filter_string = filter_features(features, filter_method)
                        if issparse(features):
                            filter_string = "chi2"
                            X_train, X_test = community_weighting(X_train, X_test, y_train)
                        else:
                            filter_string = ""

                        path = get_memory_path() + "/ASU/" + dataset + "/predictions/" + method_string + "_" + filter_string + "_" + classifier_string + str(percentage) + "_" + str(trial) + "_prediction"
                        hypothesis_training_time_path = get_memory_path() + "/ASU/" + dataset + "/predictions/" + method_string + "_" + filter_string + "_" + classifier_string + str(percentage) + "_" + str(trial) + "hypothesis_training_time.txt"
                        prediction_time_path = get_memory_path() + "/ASU/" + dataset + "/predictions/" + method_string + "_" + filter_string + "_" + classifier_string + str(percentage) + "_" + str(trial) + "_prediction_time.txt"
                        if not os.path.exists(path + ".h5"):
                            ####################################################################################################
                            # Train model
                            ####################################################################################################
                            # Train classifier
                            start_time = time.time()
                            model = OneVsRestClassifier(svm.LinearSVC(C=c, random_state=None, dual=False,
                                                                      fit_intercept=fit_intercept), n_jobs=THREAD_NUM)

                            model.fit(X_train, y_train)
                            hypothesis_training_time = time.time() - start_time
                            print('Model fitting time: ', hypothesis_training_time)
                            hypothesis_training_times.append(hypothesis_training_time)

                            with open(hypothesis_training_time_path, "w") as fp:
                                row = str(hypothesis_training_time)
                                fp.write(row)
                            ####################################################################################################
                            # Make predictions
                            ####################################################################################################
                            start_time = time.time()
                            y_pred = model.decision_function(X_test)
                            prediction_time = time.time() - start_time
                            print('Prediction time: ', prediction_time)
                            prediction_times.append(prediction_time)

                            with open(prediction_time_path, "w") as fp:
                                row = str(prediction_time)
                                fp.write(row)

                            # np.save(path, y_pred)
                            write_predictions(path, y_pred)
                        else:
                            file_row_gen = get_file_row_generator(hypothesis_training_time_path, "\t")
                            hypothesis_training_time = float(next(file_row_gen)[0])
                            hypothesis_training_times.append(hypothesis_training_time)

                            file_row_gen = get_file_row_generator(prediction_time_path, "\t")
                            prediction_time = float(next(file_row_gen)[0])
                            prediction_times.append(prediction_time)

                            # y_pred = np.load(path + ".npy")
                            y_pred = read_predictions(path)

                        y_pred = form_node_label_prediction_matrix(y_pred, y_test)

                        ########################################################################################################
                        # Calculate measures
                        ########################################################################################################
                        measures = evaluation.calculate_measures(y_pred, y_test)

                        macro_recall[trial] = measures[0]
                        micro_recall[trial] = measures[1]

                        macro_precision[trial] = measures[2]
                        micro_precision[trial] = measures[3]

                        macro_F1[trial] = measures[4]
                        micro_F1[trial] = measures[5]

                        trial_F1[trial, :] = measures[6]

                        print('Trial ', trial+1, ':')
                        print(' Macro-precision: ', macro_precision[trial])
                        print(' Micro-precision: ', micro_precision[trial])
                        print(' Macro-recall:    ', macro_recall[trial])
                        print(' Micro-recall:    ', micro_recall[trial])
                        print(' Macro-F1:        ', macro_F1[trial])
                        print(' Micro-F1:        ', micro_F1[trial])
                        print('\n')

                    # Store results
                    print(percentage)
                    print('\n')
                    print('Macro precision average: ', np.mean(macro_precision))
                    print('Micro precision average: ', np.mean(micro_precision))
                    print('Macro precision     std: ', np.std(macro_precision))
                    print('Micro precision     std: ', np.std(micro_precision))
                    print('\n')
                    print('Macro recall    average: ', np.mean(macro_recall))
                    print('Micro recall    average: ', np.mean(micro_recall))
                    print('Macro recall        std: ', np.std(macro_recall))
                    print('Micro recall        std: ', np.std(micro_recall))
                    print('\n')
                    print('Macro F1        average: ', np.mean(macro_F1))
                    print('Micro F1        average: ', np.mean(micro_F1))
                    print('Macro F1            std: ', np.std(macro_F1))
                    print('Micro F1            std: ', np.std(micro_F1))

                    mean_macro_precision[p] = np.mean(macro_precision)
                    mean_micro_precision[p] = np.mean(micro_precision)
                    mean_macro_recall[p] = np.mean(macro_recall)
                    mean_micro_recall[p] = np.mean(micro_recall)
                    mean_macro_F1[p] = np.mean(macro_F1)
                    mean_micro_F1[p] = np.mean(micro_F1)
                    F1[p, :] = np.mean(trial_F1, axis=0)

                    # Store model time
                    prediction_time_path = get_memory_path() + "/ASU/" + dataset + "/prediction_times/" + method_string + "_" + filter_string + "_" + classifier_string + str(percentage) + "_" + str(trial) + "_prediction_time.txt"
                    with open(prediction_time_path, "w") as fp:
                        row = "Hypothesis training times" + "\n"
                        fp.write(row)
                        row = "\t".join(str(t) for t in hypothesis_training_times) + "\n"
                        fp.write(row)
                        row = "Prediction times" + "\n"
                        fp.write(row)
                        row = "\t".join(str(t) for t in prediction_times) + "\n"
                        fp.write(row)
                        row = "Hypothesis training times STATS" + "\n"
                        fp.write(row)
                        row = str(statistics.mean(hypothesis_training_times)) + "\t" + str(statistics.pstdev(hypothesis_training_times)) + "\n"
                        fp.write(row)
                        row = "Prediction times STATS" + "\n"
                        fp.write(row)
                        row = str(statistics.mean(prediction_times)) + "\t" + str(statistics.pstdev(prediction_times))
                        fp.write(row)

                measure_list = [mean_macro_precision,
                                mean_micro_precision,
                                mean_macro_recall,
                                mean_micro_recall,
                                mean_macro_F1,
                                mean_micro_F1,
                                F1]

                store_performace_measures(measure_list,
                                            get_memory_path() + "/ASU/" + dataset,
                                            method_string + "_" + filter_string + "_" + classifier_string)

########################################################################################################################
# Superscript - BlogCatalog
########################################################################################################################
# # Choose the dataset
# DATASET = "BlogCatalog"
#
# # Select the training percentages
# PERCENTAGES = np.concatenate([np.arange(1, 11), np.arange(20, 100, 10)])  # [1, 10]
#
# # Select feature extraction method
# # METHODS = ["ARCTE", "LAPEIG", "DEEPWALK", "MROC", "EDGECLUSTER", "RWMODMAX", "REPEIG", "LOUVAIN", "OSLOM", "BASECOMM", "BIGCLAM"]
# METHODS = ["DEEPWALK"]
#
# FEATURE_EXTRACTION_PARAMS = dict()
# FEATURE_EXTRACTION_PARAMS["ARCTE"] = [("rho", [0.1, 0.2, 0.3]), ("eps", [0.00001, 0.00000001])]
# FEATURE_EXTRACTION_PARAMS["LAPEIG"] = [("dim", [200, 300]), ]
# FEATURE_EXTRACTION_PARAMS["DEEPWALK"] = [("walks", [80, ]), ("window", [10, ]), ("dim", [128, ])]
# FEATURE_EXTRACTION_PARAMS["MROC"] = []
# FEATURE_EXTRACTION_PARAMS["EDGECLUSTER"] = [("dim", [5000, ]), ]
# FEATURE_EXTRACTION_PARAMS["RWMODMAX"] = [("dim", [200, ]), ]
# FEATURE_EXTRACTION_PARAMS["REPEIG"] = [("dim", [200, 300]), ]
# FEATURE_EXTRACTION_PARAMS["LOUVAIN"] = []
# FEATURE_EXTRACTION_PARAMS["OSLOM"] = [("r", [50, ]), ("hr", [50, ])]
# FEATURE_EXTRACTION_PARAMS["BASECOMM"] = []
# FEATURE_EXTRACTION_PARAMS["BIGCLAM"] = [("dim", [40, ]), ]
#
# FEATURE_FILTERING_PARAMS = dict()
# FEATURE_FILTERING_PARAMS["ARCTE"] = [True, False]
# FEATURE_FILTERING_PARAMS["LAPEIG"] = [False]
# FEATURE_FILTERING_PARAMS["DEEPWALK"] = [True, False]
# FEATURE_FILTERING_PARAMS["MROC"] = [True, False]
# FEATURE_FILTERING_PARAMS["EDGECLUSTER"] = [True, False]
# FEATURE_FILTERING_PARAMS["RWMODMAX"] = [False, ]
# FEATURE_FILTERING_PARAMS["REPEIG"] = [False, ]
# FEATURE_FILTERING_PARAMS["LOUVAIN"] = [True, False]
# FEATURE_FILTERING_PARAMS["OSLOM"] = [True, False]
# FEATURE_FILTERING_PARAMS["BASECOMM"] = [True, False]
# FEATURE_FILTERING_PARAMS["BIGCLAM"] = [True, False]
#
# CLASSIFIER_PARAMS = dict()
# CLASSIFIER_PARAMS["ARCTE"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [True, False])]
# CLASSIFIER_PARAMS["LAPEIG"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [False, ])]
# CLASSIFIER_PARAMS["DEEPWALK"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [True, False])]
# CLASSIFIER_PARAMS["MROC"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [True, False])]
# CLASSIFIER_PARAMS["EDGECLUSTER"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [True, False])]
# CLASSIFIER_PARAMS["RWMODMAX"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [False, ])]
# CLASSIFIER_PARAMS["REPEIG"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [False, ])]
# CLASSIFIER_PARAMS["LOUVAIN"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [True, False])]
# CLASSIFIER_PARAMS["OSLOM"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [True, False])]
# CLASSIFIER_PARAMS["BASECOMM"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [True, False])]
# CLASSIFIER_PARAMS["BIGCLAM"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [True, False])]
#
# TRIAL_NUM = 10
# THREAD_NUM = get_threads_number()
#
# run_asu_experiment(dataset=DATASET,
#                    percentages=PERCENTAGES,
#                    methods=METHODS,
#                    trial_num=TRIAL_NUM,
#                    feature_extraction_params=FEATURE_EXTRACTION_PARAMS,
#                    classifier_params=CLASSIFIER_PARAMS)

########################################################################################################################
# Superscript - Flickr
########################################################################################################################
# Choose the dataset
DATASET = "Flickr"  # Possible choices: BlogCatalog, Flickr, YouTube

# Select the training percentages
PERCENTAGES = np.arange(1, 11)  # [1, 10]

# Select feature extraction method
# METHODS = ["ARCTE", "LAPEIG", "DEEPWALK", "MROC", "EDGECLUSTER", "RWMODMAX", "REPEIG", "LOUVAIN", "OSLOM", "BASECOMM", "BIGCLAM"]
METHODS = ["RWMODMAX"]

FEATURE_EXTRACTION_PARAMS = dict()
FEATURE_EXTRACTION_PARAMS["ARCTE"] = [("rho", [0.1, ]), ("eps", [0.00001, ])]
FEATURE_EXTRACTION_PARAMS["LAPEIG"] = [("dim", [500, ]), ]
FEATURE_EXTRACTION_PARAMS["DEEPWALK"] = [("walks", [80, ]), ("window", [10, ]), ("dim", [128, ])]
FEATURE_EXTRACTION_PARAMS["MROC"] = []
FEATURE_EXTRACTION_PARAMS["EDGECLUSTER"] = [("dim", [10000, ]), ]
FEATURE_EXTRACTION_PARAMS["RWMODMAX"] = [("dim", [1000, ]), ]
FEATURE_EXTRACTION_PARAMS["REPEIG"] = [("dim", [200, 500, 1000]), ]
FEATURE_EXTRACTION_PARAMS["LOUVAIN"] = []
FEATURE_EXTRACTION_PARAMS["OSLOM"] = [("r", [10, ]), ("hr", [10, ])]
FEATURE_EXTRACTION_PARAMS["BASECOMM"] = []
FEATURE_EXTRACTION_PARAMS["BIGCLAM"] = [("dim", [50, ]), ]

FEATURE_FILTERING_PARAMS = dict()
FEATURE_FILTERING_PARAMS["ARCTE"] = [True, False]
FEATURE_FILTERING_PARAMS["LAPEIG"] = [False]
FEATURE_FILTERING_PARAMS["DEEPWALK"] = [True, False]
FEATURE_FILTERING_PARAMS["MROC"] = [True, False]
FEATURE_FILTERING_PARAMS["EDGECLUSTER"] = [True, False]
FEATURE_FILTERING_PARAMS["RWMODMAX"] = [True, False]
FEATURE_FILTERING_PARAMS["REPEIG"] = [False]
FEATURE_FILTERING_PARAMS["LOUVAIN"] = [True, False]
FEATURE_FILTERING_PARAMS["OSLOM"] = [True, False]
FEATURE_FILTERING_PARAMS["BASECOMM"] = [True, False]
FEATURE_FILTERING_PARAMS["BIGCLAM"] = [True, False]

CLASSIFIER_PARAMS = dict()
CLASSIFIER_PARAMS["ARCTE"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [True, False])]
CLASSIFIER_PARAMS["LAPEIG"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [False, ])]
CLASSIFIER_PARAMS["DEEPWALK"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [False, ])]
CLASSIFIER_PARAMS["MROC"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [True, False])]
CLASSIFIER_PARAMS["EDGECLUSTER"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [True, False])]
CLASSIFIER_PARAMS["RWMODMAX"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [False, ])]
CLASSIFIER_PARAMS["REPEIG"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [False, ])]
CLASSIFIER_PARAMS["LOUVAIN"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [True, False])]
CLASSIFIER_PARAMS["OSLOM"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [True, False])]
CLASSIFIER_PARAMS["BASECOMM"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [True, False])]
CLASSIFIER_PARAMS["BIGCLAM"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [True, False])]

TRIAL_NUM = 10
THREAD_NUM = get_threads_number()

run_asu_experiment(dataset=DATASET, percentages=PERCENTAGES, methods=METHODS, trial_num=TRIAL_NUM, feature_extraction_params=FEATURE_EXTRACTION_PARAMS, classifier_params=CLASSIFIER_PARAMS)

########################################################################################################################
# Superscript - YouTube
########################################################################################################################
# # Choose the dataset
# DATASET = "YouTube_cc"  # Possible choices: BlogCatalog, Flickr, YouTube
#
# # Select the training percentages
# PERCENTAGES = np.arange(1, 11)  # [1, 10]
#
# # Select feature extraction method
# METHODS = ["DEEPWALK", "REPEIG", "LAPEIG"]
#
# FEATURE_EXTRACTION_PARAMS = dict()
# FEATURE_EXTRACTION_PARAMS["ARCTE"] = [("rho", [0.1, ]), ("eps", [0.00001, ])]
# FEATURE_EXTRACTION_PARAMS["LAPEIG"] = [("dim", [50, 200, 500]), ]
# FEATURE_EXTRACTION_PARAMS["DEEPWALK"] = [("walks", [80, ]), ("window", [10, ]), ("dim", [128, ])]
# FEATURE_EXTRACTION_PARAMS["MROC"] = []
# FEATURE_EXTRACTION_PARAMS["EDGECLUSTER"] = [("dim", [1000, ]), ]
# FEATURE_EXTRACTION_PARAMS["REPEIG"] = [("dim", [50, 200, 500]), ]
# FEATURE_EXTRACTION_PARAMS["LOUVAIN"] = []
# FEATURE_EXTRACTION_PARAMS["OSLOM"] = [("r", [10, ]), ("hr", [10, ])]
# FEATURE_EXTRACTION_PARAMS["BASECOMM"] = []
# FEATURE_EXTRACTION_PARAMS["BIGCLAM"] = [("dim", [500, ]), ]
#
# FEATURE_FILTERING_PARAMS = dict()
# FEATURE_FILTERING_PARAMS["ARCTE"] = [True, False]
# FEATURE_FILTERING_PARAMS["LAPEIG"] = [False]
# FEATURE_FILTERING_PARAMS["DEEPWALK"] = [True, False]
# FEATURE_FILTERING_PARAMS["MROC"] = [True, False]
# FEATURE_FILTERING_PARAMS["EDGECLUSTER"] = [True, False]
# FEATURE_FILTERING_PARAMS["RWMODMAX"] = [True, False]
# FEATURE_FILTERING_PARAMS["REPEIG"] = [False]
# FEATURE_FILTERING_PARAMS["LOUVAIN"] = [True, False]
# FEATURE_FILTERING_PARAMS["OSLOM"] = [True, False]
# FEATURE_FILTERING_PARAMS["BASECOMM"] = [True, False]
# FEATURE_FILTERING_PARAMS["BIGCLAM"] = [True, False]
#
# CLASSIFIER_PARAMS = dict()
# CLASSIFIER_PARAMS["ARCTE"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [True, False])]
# CLASSIFIER_PARAMS["LAPEIG"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [False, ])]
# CLASSIFIER_PARAMS["DEEPWALK"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [False, ])]
# CLASSIFIER_PARAMS["MROC"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [True, False])]
# CLASSIFIER_PARAMS["EDGECLUSTER"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [True, False])]
# CLASSIFIER_PARAMS["RWMODMAX"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [False, ])]
# CLASSIFIER_PARAMS["REPEIG"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [False, ])]
# CLASSIFIER_PARAMS["LOUVAIN"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [True, False])]
# CLASSIFIER_PARAMS["OSLOM"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [True, False])]
# CLASSIFIER_PARAMS["BASECOMM"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [True, False])]
# CLASSIFIER_PARAMS["BIGCLAM"] = [("C", [1, 5, 10, 50, 100, 200, 500, 1000]), ("intercept", [True, False])]
#
# TRIAL_NUM = 10
# THREAD_NUM = get_threads_number()
#
# run_asu_experiment(dataset=DATASET, percentages=PERCENTAGES, methods=METHODS, trial_num=TRIAL_NUM, feature_extraction_params=FEATURE_EXTRACTION_PARAMS, classifier_params=CLASSIFIER_PARAMS)
