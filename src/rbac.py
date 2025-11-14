"""
rbac.py
--------
Role-based access control for scoping datasets based on admin permissions.
"""
from __future__ import annotations
from dataclasses import dataclass
import pandas as pd

@dataclass
class Admin:
    name: str
    allowed_grades: list[str]
    allowed_classes: list[str]
    region: str


def filter_by_admin_scope(df: pd.DataFrame, admin: Admin) -> pd.DataFrame:
    """Filter DataFrame by admin's allowed grades, classes, and region.

    Enforces:
      grade ∈ allowed_grades AND class ∈ allowed_classes AND region == admin.region
    """
    if df.empty:
        return df

    grade_mask = df["grade"].isin(admin.allowed_grades)
    class_mask = df["class"].isin(admin.allowed_classes)
    region_mask = df["region"].eq(admin.region)

    return df[grade_mask & class_mask & region_mask]
