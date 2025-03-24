"""
This module adds a sitecustomize hook to Ray to allow setting the current
placement group from an environment variable.
"""

import json
import os

try:
    from ray.util import (
        get_current_placement_group as original_get_current_placement_group,
        placement_group,
    )

    RAY_AVAILABLE = True
except ImportError:
    RAY_AVAILABLE = False
    original_get_current_placement_group = None
    placement_group = None

_cached_pg = None


def bundles_env_aware_get_current_placement_group():
    if not RAY_AVAILABLE:
        return None

    global _cached_pg
    RAY_PG_BUNDLES_ENV = "GPUSTACK_RAY_PLACEMENT_GROUP_BUNDLES"
    if os.environ.get(RAY_PG_BUNDLES_ENV):
        if _cached_pg is None:
            try:
                _cached_pg = placement_group(json.loads(os.environ[RAY_PG_BUNDLES_ENV]))
            except Exception as e:
                raise ValueError(
                    f"Fail to create placement group from {RAY_PG_BUNDLES_ENV} environment variable: {e}"
                )

        return _cached_pg

    return original_get_current_placement_group()


if RAY_AVAILABLE:
    import ray.util

    ray.util.get_current_placement_group = bundles_env_aware_get_current_placement_group
