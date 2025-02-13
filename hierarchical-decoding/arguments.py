""" File to hold arguments """
import argparse

# data arguments

parser = argparse.ArgumentParser(description="Main Arguments")

parser.add_argument(
  '-train-src', '--train_source', type=str, nargs='*', required=False, help='Path to train source dataset')
parser.add_argument(
  '-train-tgt', '--train_target', type=str, nargs='*', required=False, help='Path to train target dataset')

parser.add_argument(
  '-dev-src', '--dev_source', type=str, nargs='*', required=False, help='Path to train source dataset')
parser.add_argument(
  '-dev-tgt', '--dev_target', type=str, nargs='*', required=False, help='Path to train target dataset')

parser.add_argument(
  '-eval','--eval', type=str, nargs='*', required=False, help='Path to the Dev set')
parser.add_argument(
  '-eval_ref','--eval_ref', type=str, nargs='*', required=False, help='Path to the Dev set gold-standards')
parser.add_argument(
  '-test','--test', type=str, nargs='*', required=False, help='Path to the Test set')
parser.add_argument(
  '-test_ref','--test_ref', type=str, nargs='*', required=False, help='Path to the Test set gold-standards')

# training parameters
parser.add_argument(
  '-steps', '--steps', type=int, required=False, help='Number of training steps')
parser.add_argument(
  '-print-every', '--print_every', type=int, required=False, help='Print the loss/ppl every training steps')
parser.add_argument(
  '-warmup-steps', '--warmup-steps', type=int, required=False, default=4000, help='warmup steps for transformer model')
parser.add_argument(
  '-eval-steps', '--eval_steps', type=int, required=False, help='Evaluate every x steps. After that, change the task (in mtl setting)')

#parser.add_argument(
#  '--checkpoint', type=int, required=False, help='Save checkpoint every these steps')
#parser.add_argument(
#  '--checkpoint_dir', type=str, required=False, help='Path to checkpoints')

parser.add_argument(
  '-batch-size', '--batch_size', type=int, required=False, default=64, help='Batch size')
parser.add_argument(
  '-max-length', '--max_length', type=int, required=False, default=180, help='Max length in encoder/decoder')

parser.add_argument(
  '-hidden-size', '--hidden_size', type=int, required=False, help='Size of hidden layer output')
parser.add_argument(
  '-enc-filter-size', '--encoder_ff_size', type=int, required=False, help='Size of FFN Filters (Encoder)')
parser.add_argument(
  '-enc-layers', '--encoder_layer', type=int, required=False, help='Number of layers in Encoder')
parser.add_argument(
  '-enc-num-heads', '--encoder_head', type=int, required=False, help='Number of heads in self-attention in Encoder')
parser.add_argument(
  '-enc-dropout', '--encoder_dropout', type=float, required=False, help='Dropout rate in Encoder')

parser.add_argument(
  '-dec-filter-size', '--decoder_ff_size', type=int, required=False, help='Size of FFN Filters (Decoder)')
parser.add_argument(
  '-dec-layers', '--decoder_layer', type=int, required=False, help='Number of layers in Decoder')
parser.add_argument(
  '-dec-num-heads', '--decoder_head', type=int, required=False, help='Number of heads in self-attention in Decoder')
parser.add_argument(
  '-dec-dropout', '--decoder_dropout', type=float, required=False, help='Dropout rate in Decoder')


# hyper-parameters
parser.add_argument(
  '-optimizer','--optimizer', type=str, required=False, help='Optimizer that will be used')
parser.add_argument(
  '-lr','--learning_rate', type=float, required=False, default=0.0005, help='Learning rate')

parser.add_argument(
  '-beam-size','--beam_size', type=int, required=False, default=1, help='Beam search size ')
parser.add_argument(
  '-beam-alpha', '--beam_alpha', type=float, required=False, default=0.2, help='Alpha value for Beam search')

parser.add_argument(
  '-seed', '--seed', type=int, required=False, help='Seed')
parser.add_argument(
  '-mtl','--mtl', action='store_true', required=False, help='Multitask learning or not')
parser.add_argument(
  '-gpu','--gpu', action='store_true', required=False, help='Use GPU or CPU')
parser.add_argument(
  '-save-dir','--save_dir', type=str, required=True, default="/content/", help='Output directory')


parser.add_argument(
  '-model','--model', type=str, required=False, help='Path for a pre-trained model file (just to perform transfer learning)')

parser.add_argument(
  '-load-encoder','--load-encoder', action='store_true', required=False, help='Recover the encoder part (just in case a model is passed as parameter')

parser.add_argument(
  '-src-vocab','--src-vocab', type=str, nargs='*', required=False, help='source vocabulary (ies)')
parser.add_argument(
  '-tgt-vocab','--tgt-vocab', type=str, nargs='*', required=False, help='Target vocabulary (ies)')

parser.add_argument(
  '-tie-embeddings','--tie-embeddings', action='store_true', required=False, help='Tied embeddings')
parser.add_argument(
  '-patience','--patience', type=int, required=False, default=30, help='Patience to stop training')

parser.add_argument(
  '-translate','--translate', action='store_true', required=False, help='Only translate using all parameters and the pre-trained model')

parser.add_argument(
  '-params','--params', type=str, required=False, help='a json file that contains the parameters of he model')
parser.add_argument(
  '-task-id','--task-id', type=int, required=False, default=0, help='The task id that we need to use in translation mode (default:0)')

parser.add_argument(
  '-input','--input', type=str, required=False, help='Path to the input file')

# inference parameters

def get_args():
  args = parser.parse_args()
  return args

