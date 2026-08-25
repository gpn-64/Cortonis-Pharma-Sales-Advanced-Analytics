"""Customer segmentation with RFM features and deterministic segment labels."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


SEGMENT_NAMES = {
    (True, "high"): "Comptes Strategiques (Key Accounts)",
    (True, "low"): "Coeur de Portefeuille (Core Active)",
    (False, "high"): "Dormants a Haut Potentiel (Win-back prioritaire)",
    (False, "low"): "Dormants a Faible Valeur",
}


def build_rfm(transactions: pd.DataFrame, analysis_date: str | pd.Timestamp) -> pd.DataFrame:
    """Aggregate canonical transactions to one row per customer."""

    analysis_date = pd.Timestamp(analysis_date)
    rows = transactions.copy()
    rows["Date"] = pd.to_datetime(rows["Date"])
    rows["MonthPeriod"] = rows["Date"].dt.to_period("M")

    grouped = rows.groupby("Customer Name", dropna=False)
    rfm = grouped.agg(
        Country=("Country", "first"),
        City=("City", "first"),
        Channel=("Channel", "first"),
        SubChannel=("SubChannel", "first"),
        LastOrderDate=("Date", "max"),
        Frequency=("Customer Name", "size"),
        Monetary=("Sales", "sum"),
        ActiveMonths=("MonthPeriod", "nunique"),
    ).reset_index()
    rfm["Recency"] = ((analysis_date - rfm["LastOrderDate"]).dt.days // 30) + 1
    rfm["MonthlyOrderRate"] = rfm["Frequency"] / rfm["ActiveMonths"]
    rfm["MonthlyRevenueRate"] = rfm["Monetary"] / rfm["ActiveMonths"]
    rfm["AvgOrderValue"] = rfm["Monetary"] / rfm["Frequency"]
    return rfm.drop(columns="LastOrderDate")


def choose_k(rfm: pd.DataFrame, candidates=range(2, 9), random_state: int = 42) -> pd.DataFrame:
    """Return silhouette scores for candidate K-Means cluster counts."""

    features = _scaled_features(rfm)
    scores = []
    for cluster_count in candidates:
        model = KMeans(n_clusters=cluster_count, n_init=20, random_state=random_state)
        labels = model.fit_predict(features)
        scores.append({"k": cluster_count, "silhouette": silhouette_score(features, labels)})
    return pd.DataFrame(scores)


def fit_segments(
    rfm: pd.DataFrame,
    n_clusters: int = 4,
    random_state: int = 42,
) -> tuple[pd.DataFrame, KMeans, StandardScaler]:
    """Fit K-Means and apply stable business labels to its clusters."""

    result = rfm.copy()
    scaler = StandardScaler()
    features = _feature_frame(result)
    scaled_features = scaler.fit_transform(features)
    model = KMeans(n_clusters=n_clusters, n_init=20, random_state=random_state)
    result["Cluster"] = model.fit_predict(scaled_features)

    active_cutoff = result["Recency"].median()
    result["IsActive"] = result["Recency"] <= active_cutoff
    result["Status"] = np.where(result["IsActive"], "Actifs", "Dormants")
    result["Segment"] = _label_segments(result)
    return result, model, scaler


def profile_segments(segmented: pd.DataFrame) -> pd.DataFrame:
    """Build the summary table used by reporting and Power BI."""

    total_revenue = segmented["Monetary"].sum()
    profile = (
        segmented.groupby(["IsActive", "Status", "Segment"], as_index=False)
        .agg(
            n=("Customer Name", "size"),
            Recency=("Recency", "mean"),
            Frequency=("Frequency", "mean"),
            Monetary=("Monetary", "mean"),
            MonthlyRevenueRate=("MonthlyRevenueRate", "mean"),
            ActiveMonths=("ActiveMonths", "mean"),
            Revenue=("Monetary", "sum"),
        )
    )
    profile["SharePctCustomers"] = profile["n"] / len(segmented) * 100
    profile["SharePctRevenue"] = profile["Revenue"] / total_revenue * 100
    return profile.drop(columns="Revenue")


def _feature_frame(rfm: pd.DataFrame) -> pd.DataFrame:
    features = rfm[["Recency", "Frequency", "Monetary"]].astype(float).copy()
    features["Frequency"] = np.log1p(features["Frequency"])
    features["Monetary"] = np.log1p(features["Monetary"])
    return features


def _scaled_features(rfm: pd.DataFrame) -> np.ndarray:
    return StandardScaler().fit_transform(_feature_frame(rfm))


def _label_segments(segmented: pd.DataFrame) -> pd.Series:
    cluster_summary = segmented.groupby(["Cluster", "IsActive"], as_index=False).agg(
        cluster_monthly_rate=("MonthlyRevenueRate", "mean")
    )
    cluster_summary["value_band"] = "low"
    for is_active, group in cluster_summary.groupby("IsActive", sort=False):
        highest_cluster = group["cluster_monthly_rate"].idxmax()
        cluster_summary.loc[highest_cluster, "value_band"] = "high"

    labels_by_cluster = {
        row.Cluster: SEGMENT_NAMES[(bool(row.IsActive), str(row.value_band))]
        for row in cluster_summary.itertuples()
    }
    labels = segmented["Cluster"].map(labels_by_cluster)
    return labels
