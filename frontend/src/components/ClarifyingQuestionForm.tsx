"use client";

import { useState } from "react";
import type { ClarifyingQuestion, ScenarioProfileCreate } from "@/types/api";
import {
  BUDGET_LABELS,
  COMPANY_SIZE_LABELS,
  GOAL_OPTIONS,
  MATURITY_LABELS,
} from "@/lib/labels";
import { Button } from "@/components/ui/Button";

interface ClarifyingQuestionFormProps {
  questions: ClarifyingQuestion[];
  profile: ScenarioProfileCreate;
  onSubmit: (profile: ScenarioProfileCreate) => Promise<void>;
  loading?: boolean;
}

function fieldLabel(field: string): string {
  return field.replace(/_/g, " ");
}

export function ClarifyingQuestionForm({
  questions,
  profile,
  onSubmit,
  loading,
}: ClarifyingQuestionFormProps) {
  const [answers, setAnswers] = useState<Record<string, string>>({});

  function optionLabels(field: string, options: string[]): string[] {
    if (field === "company_size") {
      return options.map((value) => COMPANY_SIZE_LABELS[value as keyof typeof COMPANY_SIZE_LABELS] ?? value);
    }
    if (field === "budget_range") {
      return options.map((value) => BUDGET_LABELS[value as keyof typeof BUDGET_LABELS] ?? value);
    }
    if (field === "technical_maturity") {
      return options.map((value) => MATURITY_LABELS[value as keyof typeof MATURITY_LABELS] ?? value);
    }
    return options;
  }

  return (
    <form
      className="space-y-6"
      onSubmit={(event) => {
        event.preventDefault();
        const patch: ScenarioProfileCreate = { ...profile };
        for (const question of questions) {
          const answer = answers[question.field]?.trim();
          if (!answer) continue;
          if (question.field === "primary_goals") {
            patch.primary_goals = answer.split(",").map((item) => item.trim()).filter(Boolean);
          } else if (question.field === "free_text_summary") {
            patch.free_text_summary = answer;
          } else {
            (patch as Record<string, unknown>)[question.field] = answer;
          }
        }
        void onSubmit(patch);
      }}
    >
      {questions.map((question) => (
        <label key={question.field} className="block space-y-2">
          <span className="text-sm font-medium text-zinc-300">{question.question}</span>
          {question.options?.length ? (
            <select
              className="input-field"
              value={answers[question.field] ?? ""}
              onChange={(event) =>
                setAnswers((current) => ({ ...current, [question.field]: event.target.value }))
              }
              required
            >
              <option value="">Select {fieldLabel(question.field)}</option>
              {question.options.map((option, index) => (
                <option key={option} value={option}>
                  {optionLabels(question.field, question.options ?? [])[index]}
                </option>
              ))}
            </select>
          ) : question.field === "primary_goals" ? (
            <div className="grid gap-2 sm:grid-cols-2">
              {GOAL_OPTIONS.map((goal) => (
                <label
                  key={goal.value}
                  className="flex cursor-pointer items-center gap-2.5 rounded-lg border border-white/6 bg-white/[0.02] px-3 py-2 text-sm text-zinc-300"
                >
                  <input
                    type="checkbox"
                    className="checkbox-field"
                    checked={(answers[question.field] ?? "")
                      .split(",")
                      .filter(Boolean)
                      .includes(goal.value)}
                    onChange={(event) => {
                      const current = (answers[question.field] ?? "")
                        .split(",")
                        .filter(Boolean);
                      const next = event.target.checked
                        ? [...current, goal.value]
                        : current.filter((item) => item !== goal.value);
                      setAnswers((state) => ({
                        ...state,
                        [question.field]: next.join(","),
                      }));
                    }}
                  />
                  {goal.label}
                </label>
              ))}
            </div>
          ) : (
            <textarea
              className="input-field min-h-24 resize-y"
              value={answers[question.field] ?? ""}
              onChange={(event) =>
                setAnswers((current) => ({ ...current, [question.field]: event.target.value }))
              }
              required
            />
          )}
        </label>
      ))}

      <Button type="submit" disabled={loading}>
        {loading ? "Submitting..." : "Continue"}
      </Button>
    </form>
  );
}
