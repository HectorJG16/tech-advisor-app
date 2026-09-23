from __future__ import annotations

from schemas.advisory_report import (
    AdvisoryReport,
    AlternativePick,
    CostEstimate,
    ImplementationStep,
    RankedTool,
)
from schemas.catalog import PricingTier, ToolRecord
from schemas.scenario_profile import ScenarioProfile


def _goal_phrase(profile: ScenarioProfile) -> str:
    goals = profile.primary_goals or []
    if not goals:
        return "your automation goals"
    return ", ".join(goal.replace("_", " ") for goal in goals[:2])


def _stack_phrase(profile: ScenarioProfile) -> str:
    stack = profile.existing_stack or []
    if not stack:
        return "your current stack"
    return ", ".join(stack[:3])


def _pick_pricing_tier(profile: ScenarioProfile, tool: ToolRecord) -> PricingTier | None:
    tiers = tool.pricing_tiers
    if not tiers:
        return None

    def matches(profile_size, tier: PricingTier) -> bool:
        if not tier.company_size_fit:
            return True
        if not profile_size:
            return True
        return profile_size in tier.company_size_fit

    def within_budget(tier: PricingTier) -> bool:
        if tier.price_monthly is None:
            return profile.budget_range == "enterprise"
        if not profile.budget_range:
            return True
        price = tier.price_monthly
        budget = profile.budget_range.value
        if budget == "free":
            return price == 0
        if budget == "under_100":
            return price <= 100
        if budget == "100_to_500":
            return price <= 500
        if budget == "500_to_2000":
            return price <= 2000
        return True

    filtered = [tier for tier in tiers if matches(profile.company_size, tier) and within_budget(tier)]
    candidates = filtered or tiers
    priced = [tier for tier in candidates if tier.price_monthly is not None]
    if priced:
        return min(priced, key=lambda tier: tier.price_monthly or 0)
    return candidates[0]


def _cost_summary(tier: PricingTier, profile: ScenarioProfile) -> str:
    if tier.price_monthly is None:
        return "Custom/enterprise pricing — confirm current pricing on the vendor site."
    seat_note = " per seat" if tier.per_seat else ""
    size_note = f" for a {profile.company_size.value} team" if profile.company_size else ""
    return (
        f"Estimated ~${tier.price_monthly:.0f}/mo{seat_note}{size_note}; "
        "confirm current pricing on the vendor site."
    )


def _why_top_pick(profile: ScenarioProfile, tool: ToolRecord, fit_reason: str) -> list[str]:
    reasons: list[str] = []
    goals = profile.primary_goals or []
    if goals and tool.tags and tool.tags.goals:
        overlap = set(goals) & set(tool.tags.goals)
        if overlap:
            reasons.append(f"Matches your goal to {next(iter(overlap)).replace('_', ' ')}")
    stack = profile.existing_stack or []
    if stack and tool.tags and tool.tags.integrations:
        overlap = {item.lower() for item in stack} & {item.lower() for item in tool.tags.integrations}
        if overlap:
            reasons.append(f"Integrates with {next(iter(overlap)).title()}")
    if profile.technical_maturity and tool.tags and tool.tags.technical_maturity_fits:
        if profile.technical_maturity in tool.tags.technical_maturity_fits:
            reasons.append(f"Fits a {profile.technical_maturity.value.replace('_', ' ')} team")
    if fit_reason:
        reasons.append(fit_reason)
    if tool.pros:
        reasons.extend(tool.pros[:2])
    return reasons[:4] or [fit_reason or f"Strong overall fit for {_goal_phrase(profile)}."]


def _migration_path(profile: ScenarioProfile, tool: ToolRecord) -> list[str]:
    notes: list[str] = []
    playbook = tool.playbook
    if playbook and playbook.migration_notes:
        for stack_item in profile.existing_stack or []:
            key = stack_item.lower()
            for note_key, note_lines in playbook.migration_notes.items():
                if note_key.lower() == key:
                    notes.extend(note_lines)
        if not notes:
            for lines in playbook.migration_notes.values():
                notes.extend(lines[:1])
    if not notes:
        notes.append(f"No major migration required if starting fresh on {tool.name}.")
    return notes[:4]


def _implementation_steps(tool: ToolRecord) -> list[ImplementationStep]:
    playbook = tool.playbook
    if not playbook or not playbook.implementation_steps:
        return [
            ImplementationStep(
                step=1,
                title="Review vendor onboarding guide",
                description=f"Follow {tool.vendor}'s setup documentation for {tool.name}.",
            )
        ]
    steps: list[ImplementationStep] = []
    for item in playbook.implementation_steps:
        steps.append(
            ImplementationStep(
                step=int(item.get("step") or len(steps) + 1),
                title=str(item.get("title") or "Implementation step"),
                description=str(item.get("description") or ""),
            )
        )
    return steps


def _alternates(ranked: list[RankedTool], tools: dict[str, ToolRecord]) -> list[AlternativePick]:
    picks: list[AlternativePick] = []
    for item in ranked[1:3]:
        tool = tools.get(item.slug)
        if tool and tool.pros:
            choose_if = tool.pros[0]
        else:
            choose_if = f"You want an alternative to {ranked[0].name} with a different feature mix."
        picks.append(
            AlternativePick(
                tool_id=item.tool_id,
                slug=item.slug,
                name=item.name,
                choose_if=choose_if,
            )
        )
    return picks


def build_advisory_report(
    profile: ScenarioProfile,
    ranked_raw: list[dict],
    tools: dict[str, ToolRecord],
) -> AdvisoryReport:
    ranked_list = [
        RankedTool(
            tool_id=str(item["tool_id"]),
            slug=item["slug"],
            name=item["name"],
            score=float(item["score"]),
            fit_reason=item["fit_reason"],
        )
        for item in ranked_raw
    ]
    if not ranked_list:
        raise ValueError("Cannot build report without ranked tools")

    top = ranked_list[0]
    top_tool = tools.get(top.slug)
    if not top_tool:
        raise ValueError(f"Missing catalog record for top pick: {top.slug}")

    industry = profile.industry or "your business"
    executive_summary = (
        f"Based on your {industry} needs and {_stack_phrase(profile)}, "
        f"{top.name} is the strongest fit for {_goal_phrase(profile)}."
    )

    tier = _pick_pricing_tier(profile, top_tool)
    if tier:
        cost_estimate = CostEstimate(
            tier_name=tier.tier_name,
            price_monthly=tier.price_monthly,
            price_currency=tier.price_currency,
            per_seat=tier.per_seat,
            summary=_cost_summary(tier, profile),
        )
    else:
        cost_estimate = CostEstimate(
            tier_name="Standard",
            price_monthly=None,
            summary="Pricing varies — confirm current tiers on the vendor site.",
        )

    return AdvisoryReport(
        executive_summary=executive_summary,
        ranked_list=ranked_list,
        why_top_pick=_why_top_pick(profile, top_tool, top.fit_reason),
        cost_estimate=cost_estimate,
        implementation_steps=_implementation_steps(top_tool),
        migration_path=_migration_path(profile, top_tool),
        tradeoffs=top_tool.cons[:4] or ["Evaluate fit during a pilot before full rollout."],
        alternatives=_alternates(ranked_list, tools),
    )
