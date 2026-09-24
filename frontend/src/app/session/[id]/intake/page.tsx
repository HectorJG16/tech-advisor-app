import { IntakeFlow } from "@/components/IntakeFlow";
import type { IntakeMode } from "@/types/api";

interface IntakePageProps {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ mode?: string }>;
}

function parseMode(value: string | undefined): IntakeMode {
  if (value === "quick_ask" || value === "wizard" || value === "guided") {
    return value;
  }
  return "wizard";
}

export default async function IntakePage({ params, searchParams }: IntakePageProps) {
  const { id } = await params;
  const { mode: modeParam } = await searchParams;
  const mode = parseMode(modeParam);

  return <IntakeFlow sessionId={id} mode={mode} />;
}
