from __future__ import annotations

import json
import math
from pathlib import Path

from pydantic import BaseModel, Field

from ped_agent.catalog import Catalog


class GoldQuestion(BaseModel):
    question_id: str
    query: str
    expected_resource_ids: list[str] = Field(min_length=1)
    expected_locators: list[str] = Field(default_factory=list)


class EvaluationReport(BaseModel):
    question_count: int
    k: int
    recall_at_k: float
    mrr: float
    ndcg_at_k: float
    locator_hit_rate: float


class EvaluationAcceptanceConfig(BaseModel):
    question_count: int = Field(ge=1)
    k: int = Field(ge=1)
    minimum_recall_at_k: float = Field(ge=0, le=1)
    minimum_mrr: float = Field(ge=0, le=1)
    minimum_locator_hit_rate: float = Field(ge=0, le=1)
    maximum_non_official_leakage: float = Field(ge=0, le=1)


class EvaluationAcceptanceReport(BaseModel):
    evaluation: EvaluationReport
    non_official_leakage: float = Field(ge=0, le=1)
    errors: tuple[str, ...]

    @property
    def is_compliant(self) -> bool:
        return not self.errors


class CatalogAuditReport(BaseModel):
    resource_count: int
    official_resource_count: int
    official_chunk_count: int
    locator_coverage: float
    duplicate_sha256_count: int


def load_gold(path: Path) -> list[GoldQuestion]:
    return [
        GoldQuestion.model_validate(json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def evaluate_rankings(
    questions: list[GoldQuestion],
    rankings: dict[str, list[tuple[str, str]]],
    *,
    k: int,
) -> EvaluationReport:
    if not questions:
        raise ValueError("evaluation requires at least one Gold Question")
    if k < 1:
        raise ValueError("evaluation k must be positive")
    recalls: list[float] = []
    reciprocal_ranks: list[float] = []
    ndcgs: list[float] = []
    locator_hits: list[float] = []
    for question in questions:
        ranked = rankings.get(question.question_id, [])[:k]
        expected_resources = set(question.expected_resource_ids)
        expected_locators = set(question.expected_locators)
        recalls.append(float(any(resource_id in expected_resources for resource_id, _ in ranked)))
        rank = next(
            (
                index
                for index, (resource_id, _) in enumerate(ranked, start=1)
                if resource_id in expected_resources
            ),
            None,
        )
        reciprocal_ranks.append(0.0 if rank is None else 1.0 / rank)
        relevance = [int(resource_id in expected_resources) for resource_id, _ in ranked]
        dcg = sum(value / math.log2(index + 1) for index, value in enumerate(relevance, start=1))
        ideal_count = min(len(expected_resources), k)
        ideal_dcg = sum(1.0 / math.log2(index + 1) for index in range(1, ideal_count + 1))
        ndcgs.append(0.0 if ideal_dcg == 0 else dcg / ideal_dcg)
        locator_hits.append(
            float(
                not expected_locators
                or any(
                    resource_id in expected_resources and expected in actual
                    for resource_id, actual in ranked
                    for expected in expected_locators
                )
            )
        )
    count = len(questions)
    return EvaluationReport(
        question_count=count,
        k=k,
        recall_at_k=sum(recalls) / count,
        mrr=sum(reciprocal_ranks) / count,
        ndcg_at_k=sum(ndcgs) / count,
        locator_hit_rate=sum(locator_hits) / count,
    )


def audit_evaluation(
    report: EvaluationReport,
    config: EvaluationAcceptanceConfig,
    *,
    non_official_leakage: float,
) -> EvaluationAcceptanceReport:
    errors: list[str] = []
    if report.question_count != config.question_count:
        errors.append(f"Gold Question count must equal {config.question_count}")
    if report.k != config.k:
        errors.append(f"evaluation k must equal {config.k}")
    if report.recall_at_k < config.minimum_recall_at_k:
        errors.append(f"Recall@{config.k} is below {config.minimum_recall_at_k}")
    if report.mrr < config.minimum_mrr:
        errors.append(f"MRR is below {config.minimum_mrr}")
    if report.locator_hit_rate < config.minimum_locator_hit_rate:
        errors.append(
            f"locator hit rate is below {config.minimum_locator_hit_rate}"
        )
    if non_official_leakage > config.maximum_non_official_leakage:
        errors.append(
            "non-official leakage exceeds "
            f"{config.maximum_non_official_leakage}"
        )
    return EvaluationAcceptanceReport(
        evaluation=report,
        non_official_leakage=non_official_leakage,
        errors=tuple(errors),
    )


def audit_catalog(catalog: Catalog) -> CatalogAuditReport:
    resources = catalog.list_resources()
    chunks = catalog.list_official_chunks()
    hashes: list[str] = []
    official = 0
    for resource in resources:
        metadata = resource["canonical_metadata"]
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        hashes.append(metadata["sha256"])
        official += int(resource["retrieval_eligibility"] == "official")
    duplicate_count = len(hashes) - len(set(hashes))
    locator_coverage = (
        0.0 if not chunks else sum(bool(item["locator"]) for item in chunks) / len(chunks)
    )
    return CatalogAuditReport(
        resource_count=len(resources),
        official_resource_count=official,
        official_chunk_count=len(chunks),
        locator_coverage=locator_coverage,
        duplicate_sha256_count=duplicate_count,
    )
