"use client";

import { useState } from "react";
import type { ScenarioProfileCreate } from "@/types/api";
import { Button } from "@/components/ui/Button";

interface QuickAskFormProps {
  initialSummary?: string;
  onSubmit: (profile: ScenarioProfileCreate) => Promise<void>;
  loading?: boolean;
}

export function QuickAskForm({ initialSummary = "", onSubmit, loading }: QuickAskFormProps) {
  const [summary, setSummary] = useState(initialSummary);

  return (
    <form
      className="space-y-4"
      onSubmit={(event) => {
        event.preventDefault();
        void onSubmit({ free_text_summary: summary.trim() });
      }}
    >
      <label className="block space-y-2">
        <span className="text-sm font-medium text-slate-700">Describe your scenario</span>
        <textarea
          className="min-h-40 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none ring-teal-600 focus:ring-2"
          placeholder="Example: 5-person e-commerce store on Shopify needs AI chat for order status and returns."
          value={summary}
          onChange={(event) => setSummary(event.target.value)}
          required
        />
      </label>
      <Button type="submit" disabled={loading || !summary.trim()}>
        {loading ? "Submitting..." : "Continue"}
      </Button>
    </form>
  );
}
