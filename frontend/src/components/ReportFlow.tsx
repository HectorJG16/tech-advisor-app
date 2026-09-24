"use client";

import { useEffect, useState } from "react";
import { getRecommendations } from "@/lib/api";
import type { RecommendResponse } from "@/types/api";
import { AppShell } from "@/components/AppShell";
import { AdvisoryReportView } from "@/components/AdvisoryReportView";
import { ErrorBanner } from "@/components/ErrorBanner";
import { FeedbackBar } from "@/components/FeedbackBar";
import { Card } from "@/components/ui/Card";
import { MotionFadeIn } from "@/components/ui/MotionFadeIn";

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
      <div className="space-y-8">
        <MotionFadeIn>
          <p className="section-label">Your results</p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight md:text-4xl">
            <span className="gradient-text">Recommendations</span> ready
          </h1>
          <p className="mt-3 text-zinc-400">
            Ranked tools and a template advisory report for your scenario.
          </p>
        </MotionFadeIn>

        {loading ? (
          <Card delay={0.1}>
            <div className="flex items-center gap-4">
              <div
                className="h-10 w-10 animate-spin rounded-full border-2 border-white/10 border-t-cyan-400"
                aria-hidden
              />
              <div className="flex-1 space-y-2">
                <div className="loading-shimmer h-4 w-48 rounded-lg" />
                <div className="loading-shimmer h-3 w-64 rounded-lg opacity-60" />
              </div>
            </div>
            <p className="mt-4 text-sm text-zinc-500">Generating recommendations...</p>
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
