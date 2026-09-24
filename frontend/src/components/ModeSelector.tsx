"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { createSession } from "@/lib/api";
import { MODE_LABELS } from "@/lib/labels";
import type { IntakeMode } from "@/types/api";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ErrorBanner } from "@/components/ErrorBanner";
import { MotionFadeIn } from "@/components/ui/MotionFadeIn";

const MODES: IntakeMode[] = ["quick_ask", "wizard", "guided"];

const MODE_ICONS: Record<IntakeMode, string> = {
  quick_ask: "⚡",
  wizard: "✦",
  guided: "◎",
};

export function ModeSelector() {
  const router = useRouter();
  const [loadingMode, setLoadingMode] = useState<IntakeMode | null>(null);
  const [error, setError] = useState<unknown>(null);

  async function start(mode: IntakeMode) {
    setLoadingMode(mode);
    setError(null);
    try {
      const session = await createSession();
      router.push(`/session/${session.session_id}/intake?mode=${mode}`);
    } catch (err) {
      setError(err);
      setLoadingMode(null);
    }
  }

  return (
    <div className="space-y-10">
      <MotionFadeIn>
        <p className="section-label">Intelligent tool matching</p>
        <h1 className="mt-3 max-w-3xl text-4xl font-bold tracking-tight md:text-5xl">
          Find the right{" "}
          <span className="gradient-text">automation tools</span>
        </h1>
        <p className="mt-5 max-w-2xl text-lg leading-relaxed text-zinc-400">
          Describe your business scenario and get ranked recommendations with a
          tailored advisory report — powered by ML, not guesswork.
        </p>
      </MotionFadeIn>

      {error ? (
        <MotionFadeIn delay={0.1}>
          <ErrorBanner error={error} />
        </MotionFadeIn>
      ) : null}

      <div className="grid gap-5 md:grid-cols-3">
        {MODES.map((mode, index) => (
          <Card key={mode} hover delay={0.12 + index * 0.08} className="flex flex-col">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-lg">
              {MODE_ICONS[mode]}
            </span>
            <h2 className="mt-5 text-lg font-semibold text-zinc-100">
              {MODE_LABELS[mode].title}
            </h2>
            <p className="mt-2 flex-1 text-sm leading-6 text-zinc-400">
              {MODE_LABELS[mode].description}
            </p>
            <Button
              className="mt-6 w-full"
              disabled={loadingMode !== null}
              onClick={() => start(mode)}
            >
              {loadingMode === mode ? "Starting..." : "Start"}
            </Button>
          </Card>
        ))}
      </div>
    </div>
  );
}
