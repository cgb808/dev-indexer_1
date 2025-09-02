"""LTR Model Scaffold (Artifact B)

Simple linear model placeholder. Real implementation may load:
  * LightGBM model via pickle
  * Torch model state dict
  * ONNX runtime session

Kept minimal + dependency free for bootstrap.
"""

from __future__ import annotations

from typing import List


class LTRModel:
    def __init__(self, weights: List[float] | None = None):
        # weights length must match feature dimension; default uniform
        self.weights = weights or []

    def ensure_dim(self, dim: int):
        if not self.weights:
            self.weights = [1.0] * dim
        elif len(self.weights) != dim:
            # naive resize (truncate/pad)
            if len(self.weights) > dim:
                self.weights = self.weights[:dim]
            else:
                self.weights.extend([0.0] * (dim - len(self.weights)))

    def score_matrix(self, features: List[List[float]]) -> List[float]:
        if not features:
            return []
        self.ensure_dim(len(features[0]))
        scores: List[float] = []
        for row in features:
            s = sum(w * v for w, v in zip(self.weights, row))
            scores.append(s)
        return scores


GLOBAL_LTR_MODEL = LTRModel()
