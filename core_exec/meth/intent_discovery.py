from __future__ import annotations

import math
import random
import time
from typing import List, Sequence, Union

# intent_discovery.py
# User-Driven Intent Discovery

TextOrEmbedding = Union[str, Sequence[float]]

MODE_KEYWORDS = {
    "Writing": {"write", "story", "draft", "compose", "narrative"},
    "Research": {"search", "lookup", "research", "facts", "info"},
    "Reasoning": {"reason", "analysis", "logic", "why", "explain"},
}


class IntentDiscovery:
    """
    Implements adaptive intent discovery.
    Detects behavioral patterns and categorizes them
    into latent intent modes for downstream routing.
    """

    def __init__(self, max_samples: int = 1000, k_clusters: int = 3, max_iterations: int = 12):
        self.sample_data: List[TextOrEmbedding] = []
        self.detected_modes: List[str] = []
        self.max_samples = max_samples
        self.k_clusters = k_clusters
        self.max_iterations = max_iterations

    def collect_sample(self, vector: TextOrEmbedding) -> None:
        """Store anonymized interaction vector (text or embedding)."""
        timestamp = time.strftime("%H:%M:%S")
        self.sample_data.append(vector)
        total = len(self.sample_data)
        print(f"[IntentDiscovery] ({timestamp}) Sample collected. Total={total}")
        if total < 30:
            print("[IntentDiscovery] Aviso: la sesión tiene menos de 30 muestras; los clusters pueden ser inestables.")
        if len(self.sample_data) > self.max_samples:
            self.sample_data.pop(0)
            print("[IntentDiscovery] Sample window full; dropping oldest entry to keep session fresh.")

    def cluster_modes(self) -> List[str]:
        """Cluster stored samples and emit detected modes."""
        start = time.perf_counter()
        print("[IntentDiscovery] Clustering session embeddings...")

        if not self.sample_data:
            self.detected_modes = ["Reasoning", "Search", "Creative"]
            print("[IntentDiscovery] No samples yet; using defaults:", self.detected_modes)
            return self.detected_modes

        embeddings = [_to_embedding(sample) for sample in self.sample_data]
        labels = _kmeans(embeddings, min(self.k_clusters, len(embeddings)), self.max_iterations)
        cluster_modes = _map_clusters_to_modes(labels, self.sample_data)

        if not cluster_modes:
            cluster_modes = ["Reasoning", "Creative"]

        self.detected_modes = sorted(cluster_modes)
        duration = (time.perf_counter() - start) * 1000
        print(f"[IntentDiscovery] Modes derived: {self.detected_modes} | samples={len(self.sample_data)} | time={duration:.2f}ms")
        return self.detected_modes

    def get_modes(self) -> List[str]:
        """Return currently derived adaptive modes."""
        return self.detected_modes

    def reset_session(self) -> None:
        """Clear accumulated samples and detected modes."""
        self.sample_data.clear()
        self.detected_modes = []
        print("[IntentDiscovery] Session reset; samples cleared.")

    def embed_and_cluster(self, texts: List[TextOrEmbedding]) -> List[str]:
        """
        Run clustering from external callers that already hold the interaction batch.
        Args:
            texts: list of utterances (str) or embeddings (sequence of floats).
        Returns:
            list of detected modes (Writing/Research/Reasoning/...).
        """
        start = time.perf_counter()
        print(f"[IntentDiscovery] embed_and_cluster invoked with {len(texts)} items.")
        embeddings = [_to_embedding(item) for item in texts]
        labels = _kmeans(embeddings, min(self.k_clusters, len(embeddings)), self.max_iterations)
        modes = _map_clusters_to_modes(labels, texts)
        if not modes:
            modes = ["Reasoning", "Creative"]
        duration = (time.perf_counter() - start) * 1000
        print(f"[IntentDiscovery] embed_and_cluster result: {modes} | time={duration:.2f}ms")
        return sorted(modes)


def _to_embedding(sample: TextOrEmbedding) -> List[float]:
    if hasattr(sample, "__iter__") and not isinstance(sample, str):
        try:
            return [float(x) for x in sample]  # type: ignore[arg-type]
        except TypeError:
            pass
    text = str(sample).lower()
    features: List[float] = []
    for keyword_set in MODE_KEYWORDS.values():
        features.append(float(sum(text.count(token) for token in keyword_set)))
    features.append(float(len(text.split())))
    features.append(float(sum(ch.isdigit() for ch in text)))
    return features or [0.0]


def _kmeans(vectors: List[List[float]], k: int, max_iterations: int) -> List[int]:
    if k <= 0:
        return [0] * len(vectors)
    if len(vectors) == 1:
        return [0]

    dim = len(vectors[0])
    centers = vectors[:k]
    if len(centers) < k:
        centers = centers + [random.choice(vectors)[:] for _ in range(k - len(centers))]

    labels = [0] * len(vectors)
    for iteration in range(max_iterations):
        for idx, vec in enumerate(vectors):
            distances = [_euclidean(vec, center) for center in centers]
            labels[idx] = distances.index(min(distances))
        new_centers = [[0.0] * dim for _ in range(k)]
        counts = [0] * k
        for label, vec in zip(labels, vectors):
            counts[label] += 1
            for d in range(dim):
                new_centers[label][d] += vec[d]
        for ci in range(k):
            if counts[ci]:
                new_centers[ci] = [value / counts[ci] for value in new_centers[ci]]
            else:
                new_centers[ci] = random.choice(vectors)
        if new_centers == centers:
            break
        centers = new_centers
        print(f"[IntentDiscovery] KMeans iteration {iteration+1}/{max_iterations}")
    return labels


def _euclidean(a: List[float], b: List[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _map_clusters_to_modes(labels: List[int], samples: List[TextOrEmbedding]) -> List[str]:
    cluster_to_text = {}
    for label, sample in zip(labels, samples):
        cluster_to_text.setdefault(label, []).append(str(sample).lower())

    detected = set()
    for texts in cluster_to_text.values():
        combined = " ".join(texts)
        for mode, keywords in MODE_KEYWORDS.items():
            if any(token in combined for token in keywords):
                detected.add(mode)
    return list(detected)
