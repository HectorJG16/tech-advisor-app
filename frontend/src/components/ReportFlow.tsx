"use client";

import { useEffect, useState } from "react";
import { getRecommendations } from "@/lib/api";
import type { RecommendResponse } from "@/types/api";
import { AppShell } from "@/components/AppShell";
import { AdvisoryReportView } from "@/components/AdvisoryReportView";
import { ErrorBanner } from "@/components/ErrorBanner";
import { FeedbackBar } from "@/components/FeedbackBar";
import { Card } from "@/components/ui/Card";

interface ReportFlowProps {
  sessionId: string;
}

export function ReportFlow({ sessionId }: ReportFlowProps) {
  const [result, setResult] = useState<RecommendResponse | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const response = await getRecommendations(sessionId, {});
        if (active) setResult(response);
      } catch (err) {
        if (active) setError(err);
      } finally {
        if (active) setLoading(false);
      }
    }
    void load();
    return () => {
      active = false;
    };
  }, [sessionId]);

  return (
    <AppShell subtitle="Advisory report">
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Your recommendations</h1>
          <p className="mt-2 text-slate-600">
            Ranked tools and a template advisory report for your scenario.
          </p>
        </div>

        {loading ? (
          <Card>
            <p className="text-sm text-slate-600">Generating recommendations...</p>
          </Card>
        ) : null}

        {error ? <ErrorBanner error={error} /> : null}

        {result ? (
          <>
            <AdvisoryReportView
              report={result.report}
              modelVersion={result.model_version}
              cacheHit={result.cache_hit}
            />
            <FeedbackBar
              recommendationId={result.recommendation_id}
              rankedTools={result.report.ranked_list}
            />
          </>
        ) : null}
      </div>
    </AppShell>
  );
}
