# Pre-trained Node Embeddings - GSoC 2020 

This folder contains the code of the first part of the Google Summer of Code program. This part consists in generating pre-trained node embeddings and using them to initialize the embedding layer of the current architecture for RDF-to-Text generation.

Firstly, execute this:
```
   pip install -r requirements.txt
```


`Note`: Folder or file names are examples in the following snippets. However, the hyperparameters were the used in the experiments.


## 1) Generating a Knowledge Subgraph for WebNLG dataset

Firstly, you need to generate a subgraph of the dbpedia files using the subjects in the vocabulary of the webnlg dataset. To do this, you should run the following script:
```
cd tools
python3.6 build_subgraph_from_webnlg.py \
   -webnlg <all train/dev/test split in the WebNLG dataset. Example: dataset/challenge2020_train_dev/en/train dataset/challenge2020_train_dev/en/dev > \
   -dbpedia <put all .ttl files of the Knowledge Base> \
   -max-depth <Max. depth path per instance. Experiments were performed using 10.> \
   -output <path for saving the Knowledge subgraph>
```

## 2) Preprocessing WebNLG dataset

To preprocess the dataset and save graph nodes, edges in the processed_graphs.

```
  python preprocess.py \
    --train_src 'data/processed_data/eng/train_src' \
    --train_tgt 'data/processed_data/eng/train_tgt' \
    --eval_src 'data/processed_data/eng/eval_src' \
    --eval_tgt 'data/processed_data/eng/eval_tgt' \
    --test_src 'data/processed_data/eng/test_src' \
    --spl_sym 'data/processed_data/special_symbols' \
    --model gat --lang eng --sentencepiece True \
    --vocab_size 16000 --sentencepiece_model 'bpe' \
    --output processed_graphs
```
Note that this script will build a "vocab" folder containing the source (pickle) and target vocabulary (sentence piece model like the example)


## 3) Node embeddings generation

All algorithms to generate node embeddings are obtained from the subgraph previously generated.


### A) RDF2Vec

Folder rdf2vec contains the same code as [pyRDF2Vec] with some small modifications for generating node embeddings in the WebNLG.

To run:
```
    cd rdf2vec
    python execute.py 
       -dbpedia <path of the dbpedia file(s). Usually a .ttl> \
       -vocab <vocabulary. It will be the pickle generated by the previous step> -embed-size 300 -depth 8 \
       -algorithm rnd -walks 200 -jobs 5 -window 5 -sg \
       -max-iter 30 -negative 25 -min-count 1 -oe subgraph_embeddings -seed 13 \
       -webnlg <You can add the WebNLG folders to enrich the dbpedia files wich relations/properties \
                that are not part of the original dbpedia files. Ex. dataset/challenge2020_train_dev/en/train> 
       -sup <if you want to add a supplementary information for the WebNLG dataset (modified relations/properties). \
              Ex. ../dataset/supplementary folder>
```
This code will save the numpy array (embeddings) in the `subgraph_embeddings` folder (or other name). This represents the embedding layer for all webnlg dataset source vocabulary.

### B) PYKE

Folder pyke contains the same code as [PYKE] with some small modifications for generating node embeddings in the WebNLG.

To install: ./install_pyke.sh | conda activate pyke


To run:
```
    cd PYKE
    python execute.py --kg_path KGs/webnlg-dbpedia/subgraph_webnlg.ttl \
        --embedding_dim 300 --num_iterations 1000 --K 45 --omega 0.45557 \
        --energy_release 0.0414 --webnlg <The same idea as the rdf2vec, optional> \
        --sup <The same idea as the rdf2vec, optional> \
        --output-name <path of the output file (csv format)>
```

PYKE generates a .csv file, so, you need to run a script to get the embeddings (vocabulary in json and embedding matrix in a numpy array). Json and Numpy files will have the same name as the csv file.
```
    cd PYKE
    python get_embeddings.py -csv <csv file> -embed-size <embedding size, generated by PYKE>

```

Note that this code extract the embeddings for all vocabulary (not only the webnlg vocabulary). This way, we must run:
```
   cd tools
   python preprocessing_embeddings.py -v-in <json file which contains all the vocabulary (nodes) previously generated> \
   -w-in <numpy array which contains all the node embeddings previously generated> \
   -v-out <json file or pickle (tensorflow) of the process webnlg dataset> \
   -w-out <Numpy array containing the embeddings for v-out>
```


## 4) Training

This is an example of single training for English (default example):
```
!python 'train_single.py' \
  --train_path 'data/processed_graphs/eng/gat/train' \
  --eval_path 'data/processed_graphs/eng/gat/eval' \
  --test_path 'data/processed_graphs/eng/gat/test' \
  --src_vocab 'vocabs/gat/eng/src_vocab' \
  --tgt_vocab 'vocabs/gat/eng/train_vocab.model' \
  --batch_size 32 --enc_type gat --dec_type transformer \
  --model gat --vocab_size 16000 \
  --emb_dim 300 --hidden_size 300 --distillation False \
  --filter_size 300 --use_bias True --beam_size 5 \
  --beam_alpha 0.1 --enc_layers 6 --dec_layers 6 \
  --num_heads 4 --use_edges False --sentencepiece True \
  --steps 20000 --eval_steps 1000 --checkpoint 5000 \
  --alpha 0.2 --dropout 0.2 --sentencepiece_model bpe \
  --reg_scale 0.0 --decay_steps 5000 --learning_rate 0.001 \
  --lang eng --debug_mode False \
  --eval 'data/processed_data/eng/eval_src' \
  --eval_ref 'data/processed_data/eng/eval_tgt' \
  --save_dir 'baseline-300' --seed 13
```

If you want to use the pre-trained embeddings generated by pyke or rdf2vec, use this script.
```
!python 'train_single.py' \
  --train_path 'webnlg-2020/processed_graphs/eng/gat/train' \
  --eval_path 'webnlg-2020/processed_graphs/eng/gat/eval' \
  --test_path 'webnlg-2020/processed_graphs/eng/gat/test' \
  --src_vocab 'vocabs/gat/eng/src_vocab' \
  --tgt_vocab 'vocabs/gat/eng/train_vocab.model' \
  --batch_size 32 --enc_type gat --dec_type transformer \
  --model gat --vocab_size 16000 \
  --emb_dim 300 --hidden_size 300 --distillation False \
  `--src_emb 'embeddings/rdf2vec/subgraph_embeddings_literals_webnlg/rnd/8/200/embeddings.sg.emb300.win5.npy' --fixed_src_emb` \
  --filter_size 300 --use_bias True --beam_size 5 \
  --beam_alpha 0.1 --enc_layers 6 --dec_layers 6 \
  --num_heads 4 --use_edges False --sentencepiece True \
  --steps 20000 --eval_steps 1000 --checkpoint 5000 \
  --alpha 0.2 --dropout 0.2 --sentencepiece_model bpe \
  --reg_scale 0.0 --decay_steps 5000 --learning_rate 0.001 \
  --lang eng --debug_mode False \
  --eval 'webnlg-2020/processed_data/eng/eval_src' \
  --eval_ref 'webnlg-2020/processed_data/eng/eval_tgt' \
  --save_dir 'subgraph_embeddings_literals_webnlg_rnd8200embsg3005' --seed 13
```
Where the `src_emb` is the numpy array corresponding to the webnlg source vocabulary and `fixed_src_emb` keeps the embedding layer fixed in the training. 


[pyRDF2Vec]: https://github.com/IBCNServices/pyRDF2Vec
[PYKE]: https://github.com/dice-group/PYKE
