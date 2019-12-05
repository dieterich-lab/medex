#! /usr/bin/env python3

import argparse
import logging

import numpy as np
import pandas as pd
import scipy.io
import tqdm

import fim

from misc.graph.DimacsGraph import DimacsGraph
import misc.logging_utils as logging_utils
import misc.parallel as parallel
import misc.utils as utils

import artzebrief.data_warehouse_utils as data_warehouse_utils

logger = logging.getLogger(__name__)

default_max_partition_size = 50
default_minimum_itemset_size = 5
default_maximum_itemset_size = 10
default_support = 10

target_choices = ['all', 'maximal', 'closed', 'rules']
default_target = 'maximal'

pruning_choices = ['none', 'weak', 'strong']
default_pruning = 'strong'

def get_itemset_indices(index_fim_result):

    itemset_index, fim_result = index_fim_result
    
    entity_indices = fim_result[0]
    count = fim_result[1]
    
    ret = [
        {
            "frequent_itemset": itemset_index,
            "entity_index": entity_index
        } for entity_index in entity_indices
    ]
        
    return ret

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="This script finds frequently co-occuring itemsets from a sparse "
        "indicator matrix. It first constructs a weighted, undirected graph "
        "based on the number of times a pair of entities appear together. It then "
        "partitions this graph so that the size of the largest partitions is not "
        "\"too big.\" Finally, it looks for frequent itemsets within the partitions.")

    parser.add_argument('sparse_indicators', help="A sparse matrix in which rows "
        "correspond to patients, etc., and columns correspond to entities")
    parser.add_argument('out', help="The output csv file")

    parser.add_argument('--max-partition-size', help="The expected maximum size "
        "of the the partitions. The partitioning algorithm does not guarantee to "
        "exactly balance the partitions, so the actual maximum may be somewhat "
        "larger. The complexity of the frequent itemset-finding algorithm is "
        "related to this value.", type=int, default=default_max_partition_size)

    parser.add_argument('--min-itemset-size', help="The minimum size to consider "
        "for frequent itemsets", type=int, default=default_minimum_itemset_size)
    
    parser.add_argument('--max-itemset-size', help="The maximum size to consider "
        "for frequent itemsets", type=int, default=default_maximum_itemset_size)

    parser.add_argument('--target', help="The type of frequent item sets to find. "
        "Please see the pyfim documentation for more details.", choices=target_choices,
        default=default_target)

    parser.add_argument('--support', help="The minimum support to consider an "
        "itemset as frequenty. Positive numbers are treated as percentages, while "
        "negative numbers are treated as absolute counts.", type=int,
        default=default_support)

    parser.add_argument('--pruning', help="The pruning strategy during the "
        "frequent itemset search", choices=pruning_choices, 
        default=default_pruning)

    logging_utils.add_logging_options(parser)
    args = parser.parse_args()
    logging_utils.update_logging(args)

    msg = "Reading indicator file"
    logger.info(msg)

    sparse_patient_info = scipy.io.mmread(args.sparse_indicators).tocsr()
    num_patients = sparse_patient_info.shape[0]
    num_entities = sparse_patient_info.shape[1]

    msg = "Extracting co-occurrence matrix"
    logger.info(msg)

    vals = data_warehouse_utils.get_co_occurrence_matrix(sparse_patient_info)
    patient_observed_values, co_occurrence_matrix = vals

    msg = "Creating co-occurrence graph"
    logger.info(msg)

    co_occurrence_graph = data_warehouse_utils.get_co_occurrence_graph(co_occurrence_matrix)

    msg = "Partitioning graph"
    logger.info(msg)
    num_partitions = np.ceil(num_entities / args.max_partition_size)
    num_partitions = int(num_partitions)
    cut_weight, partitions = co_occurrence_graph.get_partitions(num_partitions)

    msg = "Finding frequent itemsets"
    logger.info(msg)

    # change the selected pruning into the int required by fim
    if args.pruning == 'none':
        prune = 0
    elif args.pruning == 'weak':
        prune = -1
    elif args.pruning == 'strong':
        prune = 1
    else:
        msg = "Invalid pruning choice: {}".format(args.pruning)
        raise ValueError(msg)

    # check the selected target to the one-letter code for fim
    target = args.target[0]

    all_frequent_itemsets = []

    for partition in range(num_partitions):
        msg = "partition: {} of {}".format(partition, num_partitions)
        logger.info(msg)
        
        partition_entities = np.where(partitions == partition)[0]
        
        partition_observations = parallel.apply_iter_simple(patient_observed_values, 
                                                              np.intersect1d, partition_entities)
        
        partition_observations_l = [list(p) for p in partition_observations]
        frequent_itemsets = fim.eclat(partition_observations_l, 
                            prune=prune, 
                            zmin=args.min_itemset_size, 
                            zmax=args.max_itemset_size, 
                            target=target, 
                            supp=args.support)

        all_frequent_itemsets.extend(frequent_itemsets)

        msg = "Number of frequent itemsets: {}".format(len(frequent_itemsets))
        logger.info(msg)

    msg = "Combining frequent itemsets into data frame"
    logger.info(msg)

    
    num_frequent_itemsets = len(all_frequent_itemsets)
    afi = zip(range(num_frequent_itemsets), all_frequent_itemsets)
    all_frequent_itemset_indices = parallel.apply_parallel_iter(afi, num_cpus,
                                                        get_itemset_indices,
                                                        progress_bar=True)

    all_frequent_itemset_indices = utils.flatten_lists(all_frequent_itemset_indices)
    afi_df = pd.DataFrame(all_frequent_itemset_indices)

    msg = "Writing frequent itemsets to disk"
    logger.info(msg)
    utils.write_df(afi_df, args.out, index=False)

  
if __name__ == '__main__':
    main()
