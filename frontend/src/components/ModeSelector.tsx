"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { createSession, ApiError } from "@/lib/api";
import { MODE_LABELS } from "@/lib/labels";
import type { IntakeMode } from "@/types/api";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ErrorBanner } from "@/components/ErrorBanner";

const MODES: IntakeMode[] = ["quick_ask", "wizard", "guided"];

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
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-slate-900">
          Find the right automation tools
        </h1>
        <p className="mt-3 max-w-2xl text-slate-600">
          Describe your business scenario and get ranked tool recommendations with a
          template advisory report.
        </p>
      </div>

      {error ? <ErrorBanner error={error} /> : null}

      <div className="grid gap-4 md:grid-cols-3">
        {MODES.map((mode) => (
          <Card key={mode} className="flex flex-col">
            <h2 className="text-lg font-medium text-slate-900">{MODE_LABELS[mode].title}</h2>
            <p className="mt-2 flex-1 text-sm leading-6 text-slate-600">
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
