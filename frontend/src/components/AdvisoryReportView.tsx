import type { AdvisoryReport } from "@/types/api";
import { formatPrice, formatScore } from "@/lib/labels";
import { Card } from "@/components/ui/Card";

interface AdvisoryReportViewProps {
  report: AdvisoryReport;
  modelVersion?: string | null;
  cacheHit?: boolean;
}

export function AdvisoryReportView({ report, modelVersion, cacheHit }: AdvisoryReportViewProps) {
  const topPick = report.ranked_list[0];

  return (
    <div className="space-y-5">
      <Card
        className="border-cyan-400/20 bg-gradient-to-br from-cyan-400/10 via-indigo-500/5 to-violet-500/10"
        delay={0}
      >
        <p className="section-label">Executive summary</p>
        <p className="mt-4 text-lg leading-8 text-zinc-200">{report.executive_summary}</p>
        <div className="mt-5 flex flex-wrap gap-2">
          {modelVersion ? (
            <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-zinc-400">
              Model: {modelVersion}
            </span>
          ) : null}
          {cacheHit ? (
            <span className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-xs text-cyan-300">
              Cached result
            </span>
          ) : null}
        </div>
      </Card>

      <Card delay={0.06}>
        <h2 className="text-lg font-semibold text-zinc-100">Ranked recommendations</h2>
        <ol className="mt-5 space-y-3">
          {report.ranked_list.map((tool, index) => (
            <li
              key={tool.tool_id}
              className={`rounded-xl border px-4 py-4 transition ${
                index === 0
                  ? "border-cyan-400/30 bg-gradient-to-r from-cyan-400/10 to-indigo-500/10 shadow-[0_0_24px_rgba(34,211,238,0.1)]"
                  : "border-white/8 bg-white/[0.02] hover:border-white/14 hover:bg-white/[0.04]"
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-medium text-zinc-100">
                    <span
                      className={
                        index === 0
                          ? "gradient-text mr-2 font-bold"
                          : "mr-2 text-zinc-500"
                      }
                    >
                      #{index + 1}
                    </span>
                    {tool.name}
                  </p>
                  <p className="mt-1.5 text-sm leading-6 text-zinc-400">{tool.fit_reason}</p>
                </div>
                <span
                  className={`shrink-0 rounded-full px-3 py-1 text-xs font-semibold ${
                    index === 0
                      ? "bg-gradient-to-r from-cyan-400/20 to-indigo-400/20 text-cyan-200"
                      : "border border-white/10 bg-white/5 text-zinc-300"
                  }`}
                >
                  {formatScore(tool.score)}
                </span>
              </div>
            </li>
          ))}
        </ol>
      </Card>

      {topPick ? (
        <Card delay={0.12}>
          <h2 className="text-lg font-semibold text-zinc-100">Why {topPick.name} fits</h2>
          <ul className="mt-4 space-y-2.5">
            {report.why_top_pick.map((item) => (
              <li key={item} className="flex gap-3 text-sm leading-6 text-zinc-300">
                <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-gradient-to-r from-cyan-400 to-violet-400" />
                {item}
              </li>
            ))}
          </ul>
        </Card>
      ) : null}

      <Card delay={0.18}>
        <h2 className="text-lg font-semibold text-zinc-100">Cost estimate</h2>
        <div className="mt-4 space-y-2 text-sm text-zinc-300">
          <p className="font-medium text-zinc-100">
            {report.cost_estimate.tier_name}
            {report.cost_estimate.price_monthly !== null
              ? ` — ${formatPrice(report.cost_estimate.price_monthly, report.cost_estimate.price_currency)}`
              : ""}
            {report.cost_estimate.per_seat ? " / seat" : ""}
          </p>
          <p className="leading-6 text-zinc-400">{report.cost_estimate.summary}</p>
        </div>
      </Card>

      <Card delay={0.24}>
        <h2 className="text-lg font-semibold text-zinc-100">Implementation steps</h2>
        <ol className="mt-5 space-y-5">
          {report.implementation_steps.map((step) => (
            <li key={step.step} className="flex gap-4">
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-cyan-400/20 to-violet-400/20 text-sm font-bold text-cyan-200 ring-1 ring-cyan-400/20">
                {step.step}
              </span>
              <div>
                <p className="font-medium text-zinc-100">{step.title}</p>
                <p className="mt-1 text-sm leading-6 text-zinc-400">{step.description}</p>
              </div>
            </li>
          ))}
        </ol>
      </Card>

      <Card delay={0.3}>
        <h2 className="text-lg font-semibold text-zinc-100">Migration path</h2>
        <ul className="mt-4 space-y-2.5">
          {report.migration_path.map((item) => (
            <li key={item} className="flex gap-3 text-sm leading-6 text-zinc-300">
              <span className="text-cyan-400">→</span>
              {item}
            </li>
          ))}
        </ul>
      </Card>

      <Card delay={0.36}>
        <h2 className="text-lg font-semibold text-zinc-100">Tradeoffs and risks</h2>
        <ul className="mt-4 space-y-2.5">
          {report.tradeoffs.map((item) => (
            <li key={item} className="flex gap-3 text-sm leading-6 text-zinc-300">
              <span className="text-amber-400/80">!</span>
              {item}
            </li>
          ))}
        </ul>
      </Card>

      {report.alternatives.length > 0 ? (
        <Card delay={0.42}>
          <h2 className="text-lg font-semibold text-zinc-100">Alternatives</h2>
          <div className="mt-4 space-y-3">
            {report.alternatives.map((alt) => (
              <div
                key={alt.tool_id}
                className="rounded-xl border border-white/8 bg-white/[0.02] px-4 py-3 transition hover:border-white/14"
              >
                <p className="font-medium text-zinc-100">{alt.name}</p>
                <p className="mt-1 text-sm text-zinc-400">{alt.choose_if}</p>
              </div>
            ))}
          </div>
        </Card>
      ) : null}
    </div>
  );
}
