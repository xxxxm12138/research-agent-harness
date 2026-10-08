"""Information-status labels (信息状态分级), the origin ceiling rule and cross-verification.

Four tiers, seven labels:

======  ===========================================
Tier    Labels
======  ===========================================
已核实   核实
公开报道  公开报道, 媒体口径
待DD     待DD, 市场线索待核验, 未公开
推演     推演
======  ===========================================

A claim can never be labelled stronger than its evidence justifies. A figure that only
appears in a company's BP, a founder interview or a chat screenshot lands in the 待DD
tier until a third party confirms it. ``核实`` needs a filing / registry record, or two
independent kinds of public source (for example the company's official announcement
plus a news report) that agree.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum


class Status(str, Enum):
    VERIFIED = "核实"
    PUBLIC = "公开报道"
    MEDIA = "媒体口径"
    LEAD = "市场线索待核验"
    PENDING_DD = "待DD"
    INFERENCE = "推演"
    UNDISCLOSED = "未公开"

    def __str__(self) -> str:
        return self.value

    @property
    def tier(self) -> str:
        return TIER[self]


TIERS = ("已核实", "公开报道", "待DD", "推演")
TIER: dict[Status, str] = {
    Status.VERIFIED: "已核实",
    Status.PUBLIC: "公开报道",
    Status.MEDIA: "公开报道",
    Status.LEAD: "待DD",
    Status.PENDING_DD: "待DD",
    Status.UNDISCLOSED: "待DD",
    Status.INFERENCE: "推演",
}
STRENGTH: dict[Status, int] = {
    Status.VERIFIED: 5,
    Status.PUBLIC: 4,
    Status.MEDIA: 3,
    Status.LEAD: 2,
    Status.PENDING_DD: 2,
    Status.INFERENCE: 1,
    Status.UNDISCLOSED: 0,
}

# origin -> (default status, strongest status the origin can justify)
ORIGIN_RULES: dict[str, tuple[Status, Status]] = {
    "filing": (Status.VERIFIED, Status.VERIFIED),  # 工商、公告、监管披露
    "registry": (Status.VERIFIED, Status.VERIFIED),
    "verified": (Status.VERIFIED, Status.VERIFIED),  # 声称已交叉核验；按所引来源复核
    "news": (Status.PUBLIC, Status.PUBLIC),
    "official": (Status.PUBLIC, Status.PUBLIC),  # 公司官网、官方发布
    "paper": (Status.PUBLIC, Status.PUBLIC),
    "media": (Status.MEDIA, Status.MEDIA),  # 自媒体、二手转述
    "screenshot": (Status.LEAD, Status.LEAD),
    "rumor": (Status.LEAD, Status.LEAD),
    "bp": (Status.PENDING_DD, Status.PENDING_DD),  # 公司自报，未经第三方核验
    "founder_claim": (Status.PENDING_DD, Status.PENDING_DD),
    "interview": (Status.PENDING_DD, Status.PENDING_DD),
    "inference": (Status.INFERENCE, Status.INFERENCE),
}
UNKNOWN_ORIGIN: tuple[Status, Status] = (Status.PENDING_DD, Status.PENDING_DD)
PUBLIC_ORIGINS = frozenset({"news", "official", "paper"})


def parse_status(value: str | Status) -> Status:
    """Accept the Chinese label, the enum name, or spacing variants such as ``待 DD``."""
    if isinstance(value, Status):
        return value
    key = value.strip().replace(" ", "").lower()
    for status in Status:
        if key in (status.value.lower(), status.name.lower()):
            return status
    raise ValueError(f"unknown status label: {value!r}")


def origin_rule(origin: str) -> tuple[Status, Status]:
    return ORIGIN_RULES.get(origin.strip().lower(), UNKNOWN_ORIGIN)


def ceiling_for_sources(origins: Iterable[str]) -> Status:
    """Strongest label the cited sources support together (the cross-verification rule).

    One source supports at most its own origin's ceiling. Two or more *different kinds*
    of public source (news, official, paper) corroborate each other up to ``核实``; two
    news stories alone do not, since they often copy the same press release.
    """
    kinds = [origin.strip().lower() for origin in origins]
    if not kinds:
        return UNKNOWN_ORIGIN[1]
    if len({kind for kind in kinds if kind in PUBLIC_ORIGINS}) >= 2:
        return Status.VERIFIED
    ceilings = [origin_rule(kind)[1] for kind in kinds if kind != "verified"]
    if not ceilings:  # "verified" is a claim about the evidence, not evidence
        return UNKNOWN_ORIGIN[1]
    return max(ceilings, key=STRENGTH.__getitem__)


@dataclass(frozen=True)
class Claim:
    text: str
    origin: str
    status: Status
    source_ids: tuple[str, ...] = ()
    kind: str = "fact"  # fact | inference | unknown
    downgraded_from: Status | None = None

    @property
    def source_id(self) -> str | None:
        return self.source_ids[0] if self.source_ids else None

    @property
    def was_downgraded(self) -> bool:
        return self.downgraded_from is not None


def over_label(claim: Claim, cited_origins: Iterable[str]) -> Status | None:
    """The ceiling the cited sources allow, if the claim's label exceeds it; else None."""
    origins = list(cited_origins)
    if not origins:
        return None
    ceiling = ceiling_for_sources(origins)
    return ceiling if STRENGTH[claim.status] > STRENGTH[ceiling] else None


def tag_claim(
    text: str,
    origin: str,
    *,
    source_id: str | None = None,
    source_ids: Iterable[str] = (),
    asserted: str | Status | None = None,
    kind: str | None = None,
) -> Claim:
    """Label a claim from its declared origin; cap any asserted status at what it supports."""
    default, ceiling = origin_rule(origin)
    status, downgraded = default, None
    if asserted is not None:
        wanted = parse_status(asserted)
        if STRENGTH[wanted] > STRENGTH[ceiling]:
            status, downgraded = ceiling, wanted
        else:
            status = wanted
    if kind is None:
        kind = "inference" if status is Status.INFERENCE else "fact"
    ids = tuple(dict.fromkeys([*([source_id] if source_id else []), *source_ids]))
    return Claim(
        text=text,
        origin=origin,
        status=status,
        source_ids=ids,
        kind=kind,
        downgraded_from=downgraded,
    )
