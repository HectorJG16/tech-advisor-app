"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { submitIntake } from "@/lib/api";
import { MODE_LABELS } from "@/lib/labels";
import type { IntakeMode, ScenarioProfileCreate } from "@/types/api";
import { AppShell } from "@/components/AppShell";
import { ClarifyingQuestionForm } from "@/components/ClarifyingQuestionForm";
import { ErrorBanner } from "@/components/ErrorBanner";
import { QuickAskForm } from "@/components/QuickAskForm";
import { WizardForm } from "@/components/WizardForm";
import { Card } from "@/components/ui/Card";
import { MotionFadeIn } from "@/components/ui/MotionFadeIn";

interface IntakeFlowProps {
  sessionId: string;
  mode: IntakeMode;
}

export function IntakeFlow({ sessionId, mode }: IntakeFlowProps) {
  const router = useRouter();
  const [profile, setProfile] = useState<ScenarioProfileCreate>({});
  const [questions, setQuestions] = useState<
    Awaited<ReturnType<typeof submitIntake>>["clarifying_questions"] | null
  >(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<unknown>(null);

  async function handleSubmit(nextProfile: ScenarioProfileCreate) {
    setLoading(true);
    setError(null);
    try {
      const response = await submitIntake(sessionId, {
        mode,
        profile: nextProfile,
      });
      setProfile(response.profile);
      if (response.ready_for_recommendation) {
        router.push(`/session/${sessionId}/report`);
        return;
      }
      setQuestions(response.clarifying_questions);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }

  const showClarifying = questions && questions.length > 0;

  return (
    <AppShell subtitle={MODE_LABELS[mode].title}>
      <div className="space-y-8">
        <MotionFadeIn>
          <p className="section-label">{MODE_LABELS[mode].title}</p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight md:text-4xl">
            Tell us about{" "}
            <span className="gradient-text">your scenario</span>
          </h1>
          <p className="mt-3 max-w-2xl text-zinc-400">{MODE_LABELS[mode].description}</p>
        </MotionFadeIn>

        {error ? <ErrorBanner error={error} /> : null}

        <Card delay={0.1}>
          {showClarifying ? (
            <>
              <h2 className="text-lg font-semibold text-zinc-100">A few more details</h2>
              <p className="mt-2 text-sm text-zinc-400">
                Answer the questions below so we can tailor recommendations.
              </p>
              <div className="mt-6">
                <ClarifyingQuestionForm
                  questions={questions}
                  profile={profile}
                  onSubmit={handleSubmit}
                  loading={loading}
                />
              </div>
            </>
          ) : mode === "quick_ask" ? (
            <QuickAskForm
              initialSummary={profile.free_text_summary ?? ""}
              onSubmit={handleSubmit}
              loading={loading}
            />
          ) : mode === "guided" ? (
            <>
              <h2 className="text-lg font-semibold text-zinc-100">Tell us about your business</h2>
              <p className="mt-2 text-sm text-zinc-400">
                Start with a short summary. We&apos;ll ask follow-up questions if needed.
              </p>
              <div className="mt-6">
                <QuickAskForm
                  initialSummary={profile.free_text_summary ?? ""}
                  onSubmit={handleSubmit}
                  loading={loading}
                />
              </div>
            </>
          ) : (
            <WizardForm initialProfile={profile} onSubmit={handleSubmit} loading={loading} />
          )}
        </Card>
      </div>
    </AppShell>
  );
}
