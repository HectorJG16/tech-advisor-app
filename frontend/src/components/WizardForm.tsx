"use client";

import { useState } from "react";
import type {
  BudgetRange,
  CompanySize,
  ScenarioProfileCreate,
  TechnicalMaturity,
} from "@/types/api";
import {
  BUDGET_LABELS,
  COMPANY_SIZE_LABELS,
  GOAL_OPTIONS,
  MATURITY_LABELS,
} from "@/lib/labels";
import { Button } from "@/components/ui/Button";

interface WizardFormProps {
  initialProfile?: ScenarioProfileCreate;
  onSubmit: (profile: ScenarioProfileCreate) => Promise<void>;
  loading?: boolean;
}

function parseList(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

export function WizardForm({ initialProfile, onSubmit, loading }: WizardFormProps) {
  const [industry, setIndustry] = useState(initialProfile?.industry ?? "");
  const [companySize, setCompanySize] = useState(initialProfile?.company_size ?? "");
  const [budgetRange, setBudgetRange] = useState(initialProfile?.budget_range ?? "");
  const [technicalMaturity, setTechnicalMaturity] = useState(
    initialProfile?.technical_maturity ?? "",
  );
  const [goals, setGoals] = useState<string[]>(initialProfile?.primary_goals ?? []);
  const [stack, setStack] = useState((initialProfile?.existing_stack ?? []).join(", "));
  const [constraints, setConstraints] = useState((initialProfile?.constraints ?? []).join(", "));
  const [summary, setSummary] = useState(initialProfile?.free_text_summary ?? "");

  function toggleGoal(goal: string) {
    setGoals((current) =>
      current.includes(goal) ? current.filter((item) => item !== goal) : [...current, goal],
    );
  }

  return (
    <form
      className="space-y-6"
      onSubmit={(event) => {
        event.preventDefault();
        void onSubmit({
          industry: industry || null,
          company_size: (companySize || null) as CompanySize | null,
          budget_range: (budgetRange || null) as BudgetRange | null,
          technical_maturity: (technicalMaturity || null) as TechnicalMaturity | null,
          primary_goals: goals,
          existing_stack: parseList(stack),
          constraints: parseList(constraints),
          free_text_summary: summary || null,
        });
      }}
    >
      <div className="grid gap-4 md:grid-cols-2">
        <label className="block space-y-2">
          <span className="text-sm font-medium text-zinc-300">Industry</span>
          <input
            className="input-field"
            value={industry}
            onChange={(event) => setIndustry(event.target.value)}
            placeholder="e-commerce, b2b_saas, ..."
          />
        </label>
        <label className="block space-y-2">
          <span className="text-sm font-medium text-zinc-300">Company size</span>
          <select
            className="input-field"
            value={companySize}
            onChange={(event) => setCompanySize(event.target.value)}
            required
          >
            <option value="">Select size</option>
            {Object.entries(COMPANY_SIZE_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <label className="block space-y-2">
          <span className="text-sm font-medium text-zinc-300">Monthly budget</span>
          <select
            className="input-field"
            value={budgetRange}
            onChange={(event) => setBudgetRange(event.target.value)}
            required
          >
            <option value="">Select budget</option>
            {Object.entries(BUDGET_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <label className="block space-y-2">
          <span className="text-sm font-medium text-zinc-300">Technical maturity</span>
          <select
            className="input-field"
            value={technicalMaturity}
            onChange={(event) => setTechnicalMaturity(event.target.value)}
          >
            <option value="">Select maturity</option>
            {Object.entries(MATURITY_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
      </div>

      <fieldset className="space-y-3">
        <legend className="text-sm font-medium text-zinc-300">Primary goals</legend>
        <div className="grid gap-2 sm:grid-cols-2">
          {GOAL_OPTIONS.map((goal) => (
            <label
              key={goal.value}
              className="flex cursor-pointer items-center gap-2.5 rounded-lg border border-white/6 bg-white/[0.02] px-3 py-2 text-sm text-zinc-300 transition hover:border-white/12 hover:bg-white/[0.04]"
            >
              <input
                type="checkbox"
                className="checkbox-field"
                checked={goals.includes(goal.value)}
                onChange={() => toggleGoal(goal.value)}
              />
              {goal.label}
            </label>
          ))}
        </div>
      </fieldset>

      <label className="block space-y-2">
        <span className="text-sm font-medium text-zinc-300">Existing stack (comma-separated)</span>
        <input
          className="input-field"
          value={stack}
          onChange={(event) => setStack(event.target.value)}
          placeholder="shopify, hubspot, slack"
        />
      </label>

      <label className="block space-y-2">
        <span className="text-sm font-medium text-zinc-300">Constraints (comma-separated)</span>
        <input
          className="input-field"
          value={constraints}
          onChange={(event) => setConstraints(event.target.value)}
          placeholder="must_integrate_hubspot, no_code_only"
        />
      </label>

      <label className="block space-y-2">
        <span className="text-sm font-medium text-zinc-300">Additional context</span>
        <textarea
          className="input-field min-h-28 resize-y"
          value={summary}
          onChange={(event) => setSummary(event.target.value)}
          placeholder="Anything else we should know about your scenario?"
        />
      </label>

      <Button type="submit" disabled={loading || goals.length === 0}>
        {loading ? "Submitting..." : "Get recommendations"}
      </Button>
    </form>
  );
}
