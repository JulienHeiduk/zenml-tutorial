"""
Module 1 — Your first ZenML pipeline.

Goal: take a plain training script and turn it into a ZenML pipeline.
Concepts: `@step`, `@pipeline`, running locally.

Run with:
    uv run python modules/01_first_pipeline/pipeline.py
    # or, inside the Docker dev container:
    make run1
"""

import pandas as pd
from sklearn.base import ClassifierMixin
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from zenml import pipeline, step


# A "step" is just a Python function with a decorator.
# ZenML will track its inputs, outputs, code, and logs.
#
# The typed tuple return is important: ZenML reads the annotation to know that
# this step produces FOUR artifacts, not a single tuple. A bare `-> tuple`
# would yield one artifact and break the unpacking in the pipeline below.
@step
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    data = load_iris(as_frame=True)
    X_train, X_test, y_train, y_test = train_test_split(
        data.data, data.target, test_size=0.2, random_state=42
    )
    return X_train, X_test, y_train, y_test


@step
def train_model(X_train, y_train) -> ClassifierMixin:
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    return model


@step
def evaluate(model: ClassifierMixin, X_test, y_test) -> float:
    accuracy = float(model.score(X_test, y_test))
    print(f"Test accuracy: {accuracy:.4f}")
    return accuracy


# A "pipeline" wires steps together. It is *also* just a Python function.
# ZenML reads this function to build the DAG — no YAML, no graph API.
@pipeline
def iris_training_pipeline():
    X_train, X_test, y_train, y_test = load_data()
    model = train_model(X_train, y_train)
    evaluate(model, X_test, y_test)


if __name__ == "__main__":
    iris_training_pipeline()
    print("\nDone. Open the dashboard to inspect this run.")
