moses="/home/marcosbc/LinearAMR/mosesdecoder"
lng="en"

project_dir="/home/marcosbc/Multilingual-RDF-Verbalizer/pytorch/"

multi_model="/home/marcosbc/model/multi"
pipeline_dir="/home/marcosbc/results/multi-pipeline"
neuralreg_dir="/home/marcosbc/reg_model/model1.dy"

for set in dev test
do

awk '$0="<ordering> "$0' $project_dir/data/en/end2end/$set.eval > $project_dir/data/en/end2end/$set.multi.eval

python $project_dir/Translate.py -input $project_dir/data/en/end2end/$set.multi.eval -gpu \
				-params $multi_model/args.json -model $multi_model/model.pt \
				-beam-size 5 -save-dir $pipeline_dir/ordering.$set -seed 13 \
				-src-vocab $project_dir/vocab/multi-tied.vocab.json -mtl

python $project_dir/utils/mapping.py data/en/end2end/$set.eval $pipeline_dir/ordering.$set ordering $pipeline_dir/ordering.mapped.$set

awk '$0="<structuring> "$0' $pipeline_dir/ordering.mapped.$set > $pipeline_dir/ordering.mapped.multi.$set

python $project_dir/Translate.py -input $pipeline_dir/ordering.mapped.multi.$set -gpu \
				-params $multi_model/args.json -model $multi_model/model.pt \
				-beam-size 5 -save-dir $pipeline_dir/structuring.$set -seed 13 \
				-src-vocab $project_dir/vocab/multi-tied.vocab.json -mtl

python $project_dir/utils/mapping.py $pipeline_dir/ordering.mapped.$set $pipeline_dir/structuring.$set structing $pipeline_dir/structuring.mapped.$set

awk '$0="<lexicalization> "$0' $pipeline_dir/structuring.mapped.$set > $pipeline_dir/structuring.mapped.multi.$set

python $project_dir/Translate.py -input $pipeline_dir/structuring.mapped.multi.$set -gpu \
				-params $multi_model/args.json -model $multi_model/model.pt \
				-beam-size 5 -save-dir $pipeline_dir/lex.$set -seed 13 \
				-src-vocab $project_dir/vocab/multi-tied.vocab.json -mtl

python $project_dir/utils/postProcessing.py -i $pipeline_dir/lex.$set -o $pipeline_dir/lexicalization.lower.$set

$moses/scripts/recaser/recase.perl --in $pipeline_dir/lexicalization.lower.$set --model $project_dir/data/en/lexicalization/case_model/moses.ini --moses $moses/bin/moses > $pipeline_dir/lexicalization.cs.$set

python $project_dir/utils/generate.py $pipeline_dir/lexicalization.cs.$set $pipeline_dir/ordering.mapped.$set $pipeline_dir/reg.$set neuralreg $neuralreg_dir $project_dir/data/en/reg

python $project_dir/utils/realization.py $pipeline_dir/reg.$set $pipeline_dir/realization.$set $project_dir/data/en/lexicalization/surfacevocab.json

$moses/scripts/tokenizer/normalize-punctuation.perl -l $lng < $pipeline_dir/realization.$set > $pipeline_dir/realization.punc.$set
$moses/scripts/tokenizer/detokenizer.perl -l $lng < $pipeline_dir/realization.punc.$set > $pipeline_dir/realization.detok.$set
$moses/scripts/recaser/detruecase.perl < $pipeline_dir/realization.detok.$set > $pipeline_dir/realization.post.$set

done
