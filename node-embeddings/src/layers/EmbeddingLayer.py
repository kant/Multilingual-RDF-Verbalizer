"""Implementation of embedding layer with shared weights."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import numpy as np

class EmbeddingSharedWeights(tf.keras.layers.Layer):
  """Calculates input embeddings and pre-softmax linear with shared weights."""

  def __init__(self, vocab_size, hidden_size, fixed=False, embedding_init=None):
    """Specify characteristic parameters of embedding layer.

    Args:
      vocab_size: Number of tokens in the embedding. (Typically ~32,000)
      hidden_size: Dimensionality of the embedding. (Typically 512 or 1024)
      trainable: fix or finetune embeddings
      embedding_init: Embedding matrix (a numpy array)
    """

    super(EmbeddingSharedWeights, self).__init__()
    self.vocab_size = vocab_size
    self.hidden_size = hidden_size
    self.fixed = fixed
    self.is_pretrained = False
    if embedding_init is not None:
        self.is_pretrained = True
        init = tf.constant_initializer(embedding_init)
    else:
        init = tf.random_normal_initializer(
          mean=0., stddev=self.hidden_size ** -0.5)

    with tf.name_scope("embedding_and_softmax"):
      # Create and initialize weights. The random normal initializer was chosen
      # arbitrarily, and works well.
      self.shared_weights = self.add_weight(
        "weights",
        shape=[self.vocab_size, self.hidden_size],
        dtype="float32",
        trainable= not self.fixed,
        initializer=init)


  def build(self, input_shape):
    """Build embedding layer."""
    super(EmbeddingSharedWeights, self).build(input_shape)

  def get_config(self):
    return {
      "vocab_size": self.vocab_size,
      "hidden_size": self.hidden_size,
    }

  def call(self, inputs, mode="embedding"):
    """Get token embeddings of inputs.

    Args:
      inputs: An int64 tensor with shape [batch_size, length]
      mode: string, a valid value is one of "embedding" and "linear".
    Returns:
      outputs: (1) If mode == "embedding", output embedding tensor, float32 with
        shape [batch_size, length, embedding_size]; (2) mode == "linear", output
        linear tensor, float32 with shape [batch_size, length, vocab_size].
    Raises:
      ValueError: if mode is not valid.
    """
    if mode == "embedding":
      return self._embedding(inputs)
    elif mode == "linear":
      return self._linear(inputs)
    else:
      raise ValueError("mode {} is not valid.".format(mode))

  def _embedding(self, inputs):
    """Applies embedding based on inputs tensor."""
    with tf.name_scope("embedding"):
      # Create binary mask of size [batch_size, length]
      mask = tf.cast(tf.not_equal(inputs, 0), tf.float32)
      embeddings = tf.gather(self.shared_weights, inputs)
      embeddings *= tf.expand_dims(mask, -1)
      # Scale embedding by the sqrt of the hidden size. This just happens when embedding init is not passed
      if not self.is_pretrained:
        embeddings *= self.hidden_size ** 0.5

      return embeddings

  def _linear(self, inputs):
    """Computes logits by running inputs through a linear layer.

    Args:
      inputs: A float32 tensor with shape [batch_size, length, hidden_size]
    Returns:
      float32 tensor with shape [batch_size, length, vocab_size].
    """
    with tf.name_scope("presoftmax_linear"):
      batch_size = tf.shape(inputs)[0]
      length = tf.shape(inputs)[1]

      x = tf.reshape(inputs, [-1, self.hidden_size])
      logits = tf.matmul(x, self.shared_weights, transpose_b=True)

      return tf.reshape(logits, [batch_size, length, self.vocab_size])
