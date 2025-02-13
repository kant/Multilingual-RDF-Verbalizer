import argparse

from helper_classes import PYKE
from helper_classes import Parser
from helper_classes import DataAnalyser
from helper_classes import PPMI
import util as ut
import numpy as np
import random
import pandas as pd
from webnlg_util import load_supplementary, load_triples_webnlg

random_state = 1
np.random.seed(random_state)
random.seed(random_state)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--kg_path", type=str, default="KGs/father.nt", nargs="?",
                        help="Path of dataset.")
    parser.add_argument("--embedding_dim", type=int, default=20, nargs="?",
                        help="Number of dimensions in embedding space.")
    parser.add_argument("--num_iterations", type=int, default=1000, nargs="?",
                        help="Number of iterations.")
    parser.add_argument("--K", type=int, default=100, nargs="?",
                        help="Number of interactions.")
    parser.add_argument("--omega", type=float, default=0.45557, nargs="?",
                        help="Omega: a constant in repulsive force calculation.")
    parser.add_argument("--energy_release", type=float, default=0.0414, nargs="?",
                        help="Energy release per iteration.")
    parser.add_argument("--eval", type=bool, default=False, nargs="?",
                        help="Perform Type prediction.")
    parser.add_argument('-webnlg', "--webnlg", nargs='*', required=False, help="WebNLG dataset (en/train en/dev ...)")
    parser.add_argument('-sup', "--supplementary", type=str, required=False, help="Folder where there are several triple modifications")
    parser.add_argument('-output-name', "--output-name", default="PYKE_50_embd.csv" , type=str, required=False, help="CSV embeddings file")

    args = parser.parse_args()
    kg_path = args.kg_path

    # DEFINE MODEL PARAMS
    K = args.K
    num_of_dims = args.embedding_dim
    bound_on_iter = args.num_iterations
    omega = args.omega
    e_release = args.energy_release

    flag_for_type_prediction = args.eval

    storage_path, experiment_folder = ut.create_experiment_folder()
    logger = ut.create_logger(name='PYKE', p=storage_path)

    logger.info('Starts')
    logger.info('Hyperparameters:  {0}'.format(args))

    parser = Parser(p_folder=storage_path, k=K)

    parser.set_logger(logger)

    parser.set_similarity_measure(PPMI)

    model = PYKE(logger=logger)

    analyser = DataAnalyser(p_folder=storage_path, logger=logger)

    extra_triples = []
    if args.supplementary is not None:
        logger.info("Loading supplementary data ...")
        lexicon_triples, substitute_triples = load_supplementary(args.supplementary)
        logger.info("Supplementary data loaded. (" + str(len(lexicon_triples)) + "lexicon triples and" + 
          str(len(substitute_triples)), "substitute triples)")
        extra_triples += [triple for triple in lexicon_triples]
        extra_triples += [triple for triple in substitute_triples]

    if args.webnlg is not None:
        logger.info("Loading WebNLG triples ...")
        webnlg_triples = load_triples_webnlg(args.webnlg)
        logger.info(str(len(webnlg_triples)) + " modified WebNLG triples loaded")
        extra_triples += [triple for triple in webnlg_triples]

    if len(extra_triples) == 0:
        holder = parser.pipeline_of_preprocessing(kg_path)
    else:
        holder = parser.pipeline_of_preprocessing(kg_path, extra_triples=extra_triples)

    vocab_size = len(holder)

    embeddings = ut.randomly_initialize_embedding_space(vocab_size, num_of_dims)

    learned_embeddings = model.pipeline_of_learning_embeddings(e=embeddings,
                                                               max_iteration=bound_on_iter,
                                                               energy_release_at_epoch=e_release,
                                                               holder=holder, omega=omega)
    del embeddings
    del holder

    vocab = ut.deserializer(path=storage_path, serialized_name='vocabulary')
    learned_embeddings.index = [i for i in vocab]
    learned_embeddings.to_csv(storage_path + '/' + args.output_name, encoding="utf-8")

    # This crude workaround performed to serialize dataframe with corresponding terms.
    learned_embeddings.index = [i for i in range(len(vocab))]

    if flag_for_type_prediction:
        analyser.perform_type_prediction(learned_embeddings)
        #analyser.perform_clustering_quality(learned_embeddings)

    # analyser.plot2D(learned_embeddings)
