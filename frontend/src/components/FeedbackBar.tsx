"use client";

import { useState } from "react";
import type { FeedbackRating, RankedTool } from "@/types/api";
import { submitFeedback } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ErrorBanner } from "@/components/ErrorBanner";

interface FeedbackBarProps {
  recommendationId: string;
  rankedTools: RankedTool[];
}

export function FeedbackBar({ recommendationId, rankedTools }: FeedbackBarProps) {
  const [rating, setRating] = useState<FeedbackRating | null>(null);
  const [selectedToolId, setSelectedToolId] = useState("");
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<unknown>(null);

  async function handleSubmit() {
    setLoading(true);
    setError(null);
    try {
      await submitFeedback({
        recommendation_id: recommendationId,
        rating,
        selected_tool_id: selectedToolId || null,
        comment: comment || null,
      });
      setSubmitted(true);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }

  if (submitted) {
    return (
      <Card className="border-teal-200 bg-teal-50/40">
        <p className="text-sm text-teal-800">Thanks — your feedback was recorded.</p>
      </Card>
    );
  }

  return (
    <Card>
      <h2 className="text-lg font-semibold text-slate-900">Was this helpful?</h2>
      {error ? <div className="mt-4"><ErrorBanner error={error} /></div> : null}
      <div className="mt-4 flex flex-wrap gap-2">
        {(["positive", "neutral", "negative"] as FeedbackRating[]).map((value) => (
          <Button
            key={value}
            type="button"
            variant={rating === value ? "primary" : "secondary"}
            onClick={() => setRating(value)}
          >
            {value}
          </Button>
        ))}
      </div>
      <label className="mt-4 block space-y-2">
        <span className="text-sm font-medium text-slate-700">Which tool did you prefer?</span>
        <select
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          value={selectedToolId}
          onChange={(event) => setSelectedToolId(event.target.value)}
        >
          <option value="">Optional</option>
          {rankedTools.map((tool) => (
            <option key={tool.tool_id} value={tool.tool_id}>
              {tool.name}
            </option>
          ))}
        </select>
      </label>
      <label className="mt-4 block space-y-2">
        <span className="text-sm font-medium text-slate-700">Comments</span>
        <textarea
          className="min-h-24 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          value={comment}
          onChange={(event) => setComment(event.target.value)}
          placeholder="Optional feedback"
        />
      </label>
      <Button className="mt-4" disabled={loading} onClick={() => void handleSubmit()}>
        {loading ? "Sending..." : "Submit feedback"}
      </Button>
    </Card>
  );
}
