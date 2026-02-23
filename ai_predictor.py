"""
Analysis module for Travel Advisories (no prediction)

This replaces the previous ML-based predictor. It focuses on
descriptive analytics and human-readable insights only.
"""
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

import pandas as pd


@dataclass
class CountryInsight:
    country: str
    avg_risk_score: Optional[float]
    risk_level_text: str
    risk_grade: str
    n_advisories: int
    has_security_issues: bool
    has_safety_issues: bool
    has_serenity_issues: bool
    latest_date: Optional[datetime]
    latest_summary: str
    security_highlights: List[str]
    dos: List[str]
    donts: List[str]


class InsightAnalyzer:
    """
    Pure analysis helper for travel advisories.

    - NO training
    - NO prediction
    - Only aggregates and interprets existing data
    """

    SECURITY_TERMS = [
        "crime",
        "terrorism",
        "kidnap",
        "kidnapping",
        "armed",
        "attack",
        "robbery",
        "violence",
        "gang",
        "cartel",
        "carjacking",
    ]

    SAFETY_TERMS = [
        "health",
        "disease",
        "epidemic",
        "pandemic",
        "covid",
        "cholera",
        "earthquake",
        "flood",
        "hurricane",
        "storm",
        "tsunami",
        "landslide",
        "wildfire",
        "dengue",
    ]

    SERENITY_TERMS = [
        "protest",
        "demonstration",
        "civil unrest",
        "riot",
        "strike",
        "political tension",
        "instability",
    ]

    DO_PATTERNS = [
        "you should",
        "it is recommended to",
        "it is advisable to",
        "travelers should",
        "you are advised to",
        "ensure that you",
        "make sure you",
        "carry",
        "keep",
        "register with",
        "monitor",
        "stay informed",
        "be sure to",
    ]

    DONT_PATTERNS = [
        "do not",
        "don't ",
        "avoid",
        "refrain from",
        "you must not",
        "never ",
        "should not",
        "are advised against",
        "must not",
        "stay away from",
    ]

    def _mk_dataframe(self, advisories: List[Dict]) -> pd.DataFrame:
        df = pd.DataFrame(advisories)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        if "scraped_at" in df.columns:
            df["scraped_at"] = pd.to_datetime(df["scraped_at"], errors="coerce")
        return df

    def _classify_dimensions_row(self, row: pd.Series) -> Dict[str, bool]:
        text = (row.get("description_cleaned") or row.get("description") or "").lower()
        kws = " ".join(row.get("keywords") or []).lower()
        all_text = text + " " + kws

        def contains_any(terms):
            return any(t in all_text for t in terms)

        return {
            "security": contains_any(self.SECURITY_TERMS),
            "safety": contains_any(self.SAFETY_TERMS),
            "serenity": contains_any(self.SERENITY_TERMS),
        }

    def _extract_sentences(self, text: str) -> List[str]:
        if not text:
            return []
        # Simple sentence splitter
        raw = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in raw if len(s.strip()) > 0]

    def _extract_dos_donts(self, descriptions: List[str]) -> Tuple[List[str], List[str]]:
        dos: List[str] = []
        donts: List[str] = []
        seen = set()

        for desc in descriptions:
            for sent in self._extract_sentences(desc):
                sent_l = sent.lower()
                if any(pat in sent_l for pat in self.DONT_PATTERNS):
                    key = ("dont", sent_l)
                    if key not in seen:
                        seen.add(key)
                        donts.append(sent)
                elif any(pat in sent_l for pat in self.DO_PATTERNS):
                    key = ("do", sent_l)
                    if key not in seen:
                        seen.add(key)
                        dos.append(sent)

        return dos[:10], donts[:10]

    def _risk_grade_from_score(self, score: Optional[float]) -> str:
        """
        Map numeric risk (1–4) into a letter grade A–E.

        A is lowest risk, E is highest risk.
        Uses threshold-based mapping:
        - 1.0 ≤ score < 1.5 → A
        - 1.5 ≤ score < 2.5 → B
        - 2.5 ≤ score < 3.5 → C
        - 3.5 ≤ score < 4.0 → D
        - score ≥ 4.0 → E
        
        Scores outside the 1–4 range are clamped.
        None or invalid values return "U" (unknown).
        """
        if score is None:
            return "U"  # Unknown

        try:
            s = float(score)
        except Exception:
            return "U"

        # clamp to expected range
        s = max(1.0, min(s, 4.0))
        
        # threshold-based mapping
        if s < 1.5:
            return "A"
        elif s < 2.5:
            return "B"
        elif s < 3.5:
            return "C"
        elif s < 4.0:
            return "D"
        else:
            return "E"

    def attach_dimensions(self, advisories: List[Dict]) -> List[Dict]:
        """
        Return a new list of advisories with boolean flags:
        - security
        - safety
        - serenity
        """
        if not advisories:
            return []

        df = self._mk_dataframe(advisories)
        dims = df.apply(self._classify_dimensions_row, axis=1, result_type="expand")
        df = pd.concat([df, dims], axis=1)
        df = df.loc[:, ~df.columns.duplicated()]
        return df.to_dict(orient="records")

    def summarize_country(
        self, advisories: List[Dict], country_normalized: str, lookback_days: int = 365
    ) -> Optional[CountryInsight]:
        """
        Build a high-level summary for a single country.
        """
        if not advisories:
            return None

        df = self._mk_dataframe(advisories)
        if "country_normalized" not in df.columns:
            return None

        df = df[df["country_normalized"] == country_normalized]
        if df.empty:
            return None

        # time filter
        cutoff = datetime.utcnow() - timedelta(days=lookback_days)
        if "date" in df.columns:
            df = df[df["date"] >= cutoff]
        if df.empty:
            return None

        # attach dimensions
        dims = df.apply(self._classify_dimensions_row, axis=1, result_type="expand")
        df = pd.concat([df, dims], axis=1)

        # compute average risk
        avg_risk = None
        if "risk_score" in df.columns:
            avg_risk = (
                df["risk_score"].replace(0, pd.NA).dropna().astype(float).mean()
            )

        if avg_risk is not None:
            if avg_risk >= 3.5:
                risk_text = "Very High"
            elif avg_risk >= 2.5:
                risk_text = "High"
            elif avg_risk >= 1.5:
                risk_text = "Moderate"
            else:
                risk_text = "Low"
        else:
            risk_text = "Unknown"

        # attach dimensions (drop any pre-existing to avoid duplicate columns)
        df = df.drop(columns=[c for c in ["security", "safety", "serenity"] if c in df.columns])
        dims = df.apply(self._classify_dimensions_row, axis=1, result_type="expand")
        df = pd.concat([df, dims], axis=1)
        df = df.loc[:, ~df.columns.duplicated()]

        latest = df.sort_values("date", ascending=False).iloc[0]
        latest_date = latest.get("date")
        desc = latest.get("description_cleaned") or latest.get("description") or ""
        if isinstance(desc, str) and len(desc) > 280:
            desc = desc[:280] + "..."

        # security highlights: top few advisory titles/snippets mentioning key terms
        highlights: List[str] = []
        for _, row in df.sort_values("date", ascending=False).head(10).iterrows():
            text = (
                row.get("description_cleaned")
                or row.get("description")
                or ""
            )
            if not text:
                continue
            low = text.lower()
            if any(term in low for term in self.SECURITY_TERMS + self.SAFETY_TERMS + self.SERENITY_TERMS):
                snippet = text[:220] + ("..." if len(text) > 220 else "")
                if snippet not in highlights:
                    highlights.append(snippet)
            if len(highlights) >= 5:
                break

        # do's and don'ts from all descriptions for this country
        all_descs = [
            (row.get("description_cleaned") or row.get("description") or "")
            for _, row in df.iterrows()
        ]
        dos, donts = self._extract_dos_donts(all_descs)

        grade = self._risk_grade_from_score(avg_risk)
        
        # Safely check for dimension columns
        has_sec = bool(df["security"].fillna(False).astype(bool).any()) if "security" in df.columns and len(df) > 0 else False
        has_safe = bool(df["safety"].fillna(False).astype(bool).any()) if "safety" in df.columns and len(df) > 0 else False
        has_ser = bool(df["serenity"].fillna(False).astype(bool).any()) if "serenity" in df.columns and len(df) > 0 else False

        return CountryInsight(
            country=country_normalized,
            avg_risk_score=float(avg_risk) if avg_risk is not None else None,
            risk_level_text=risk_text,
            risk_grade=grade,
            n_advisories=int(len(df)),
            has_security_issues=has_sec,
            has_safety_issues=has_safe,
            has_serenity_issues=has_ser,
            latest_date=latest_date.to_pydatetime() if pd.notna(latest_date) else None,
            latest_summary=desc,
            security_highlights=highlights,
            dos=dos,
            donts=donts,
        )

    def global_risk_by_country(
        self, advisories: List[Dict]
    ) -> pd.DataFrame:
        """
        Aggregate average numeric risk score per country.
        """
        if not advisories:
            return pd.DataFrame()

        df = self._mk_dataframe(advisories)
        if "country_normalized" not in df.columns or "risk_score" not in df.columns:
            return pd.DataFrame()

        agg = (
            df.groupby("country_normalized")["risk_score"]
            .mean()
            .sort_values(ascending=False)
            .reset_index()
        )
        return agg

