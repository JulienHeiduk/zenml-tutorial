"""
Module 2 — Artifacts and caching.

Goal: understand how ZenML treats step outputs as first-class, versioned artifacts,
and how caching lets you iterate fast.

Concepts: typed outputs with `Annotated`, multiple named outputs, step-level
caching, per-step resource settings.

Run it TWICE:
    uv run python modules/02_artifacts_and_caching/pipeline.py
    uv run python modules/02_artifacts_and_caching/pipeline.py   # fully cached
    # or, inside the Docker dev container:  make run2  (twice)

On the second run, every step shows "CACHED" in the dashboard: nothing
re-executes, but you still get a full lineage record. This is the payoff.
"""

from typing import Annotated

import pandas as pd
from sklearn.base import ClassifierMixin
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from zenml import pipeline, step
from zenml.config import ResourceSettings


# ------------------------------------------------------------------------- #
# Per-step resource settings.
#
# Each step can declare its own CPU/memory/GPU requirements. On the local
# orchestrator these are informational (logged + shown in the dashboard); on
# Kubernetes / Vertex / SageMaker / Kubeflow they become real resource
# requests — the orchestrator sizes a pod or VM accordingly.
#
# The value of per-step resources: in a real pipeline, `load_data` might need
# a lot of memory (big download, parse) but one CPU, while `train_model`
# needs many CPUs or a GPU. You don't have to size the *whole* pipeline for
# the heaviest step — each step asks for what it actually needs.
# ------------------------------------------------------------------------- #


# Light, I/O-bound: 1 CPU, modest memory.
@step(settings={"resources": ResourceSettings(cpu_count=1, memory="512MB")})
def load_data() -> tuple[
    Annotated[pd.DataFrame, "X_train"],
    Annotated[pd.DataFrame, "X_test"],
    Annotated[pd.Series, "y_train"],
    Annotated[pd.Series, "y_test"],
]:
    data = load_iris(as_frame=True)
    return train_test_split(data.data, data.target, test_size=0.2, random_state=42)


# CPU-heavy: give it 4 cores and more memory.
# In a real workload with `n_jobs=-1`, sklearn will use all of them.
# Swap `gpu_count=1` in for a deep-learning step.
@step(
    enable_cache=True,
    settings={
        "resources": ResourceSettings(
            cpu_count=4,
            memory="2GB",
            # gpu_count=1,  # uncomment on a GPU-enabled stack
        )
    },
)
def train_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    n_estimators: int = 50,
) -> Annotated[ClassifierMixin, "random_forest"]:
    model = RandomForestClassifier(n_estimators=n_estimators, random_state=42)
    model.fit(X_train, y_train)
    return model


# Small footprint — evaluation is cheap.
@step(settings={"resources": ResourceSettings(cpu_count=1, memory="512MB")})
def evaluate(
    model: ClassifierMixin,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> tuple[
    Annotated[float, "accuracy"],
    Annotated[pd.DataFrame, "predictions"],
]:
    accuracy = float(model.score(X_test, y_test))
    predictions = pd.DataFrame(
        {"y_true": y_test.values, "y_pred": model.predict(X_test)}
    )
    print(f"Test accuracy: {accuracy:.4f}")
    return accuracy, predictions


@pipeline
def iris_training_pipeline(n_estimators: int = 50):
    X_train, X_test, y_train, y_test = load_data()
    model = train_model(X_train, y_train, n_estimators=n_estimators)
    evaluate(model, X_test, y_test)


if __name__ == "__main__":
    # First call: everything runs.
    iris_training_pipeline()

    # Try changing n_estimators and re-running: only `train_model` and
    # `evaluate` re-execute. `load_data` stays cached.
    # iris_training_pipeline(n_estimators=100)

    print("\nRe-run this script — every step should show CACHED the second time.")
