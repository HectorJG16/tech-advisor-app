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
    <div className="space-y-6">
      <Card className="border-teal-200 bg-teal-50/40">
        <p className="text-xs font-medium uppercase tracking-wide text-teal-700">
          Executive summary
        </p>
        <p className="mt-3 text-lg leading-8 text-slate-800">{report.executive_summary}</p>
        <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-600">
          {modelVersion ? <span>Model: {modelVersion}</span> : null}
          {cacheHit ? <span>Cached result</span> : null}
        </div>
      </Card>

      <Card>
        <h2 className="text-lg font-semibold text-slate-900">Ranked recommendations</h2>
        <ol className="mt-4 space-y-3">
          {report.ranked_list.map((tool, index) => (
            <li
              key={tool.tool_id}
              className={`rounded-lg border px-4 py-3 ${
                index === 0 ? "border-teal-300 bg-teal-50/50" : "border-slate-200"
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-medium text-slate-900">
                    #{index + 1} {tool.name}
                  </p>
                  <p className="mt-1 text-sm text-slate-600">{tool.fit_reason}</p>
                </div>
                <span className="shrink-0 rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">
                  {formatScore(tool.score)}
                </span>
              </div>
            </li>
          ))}
        </ol>
      </Card>

      {topPick ? (
        <Card>
          <h2 className="text-lg font-semibold text-slate-900">Why {topPick.name} fits</h2>
          <ul className="mt-4 list-disc space-y-2 pl-5 text-sm leading-6 text-slate-700">
            {report.why_top_pick.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </Card>
      ) : null}

      <Card>
        <h2 className="text-lg font-semibold text-slate-900">Cost estimate</h2>
        <div className="mt-4 space-y-2 text-sm text-slate-700">
          <p className="font-medium text-slate-900">
            {report.cost_estimate.tier_name}
            {report.cost_estimate.price_monthly !== null
              ? ` — ${formatPrice(report.cost_estimate.price_monthly, report.cost_estimate.price_currency)}`
              : ""}
            {report.cost_estimate.per_seat ? " / seat" : ""}
          </p>
          <p>{report.cost_estimate.summary}</p>
        </div>
      </Card>

      <Card>
        <h2 className="text-lg font-semibold text-slate-900">Implementation steps</h2>
        <ol className="mt-4 space-y-4">
          {report.implementation_steps.map((step) => (
            <li key={step.step} className="flex gap-4">
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-100 text-sm font-semibold text-slate-700">
                {step.step}
              </span>
              <div>
                <p className="font-medium text-slate-900">{step.title}</p>
                <p className="mt-1 text-sm leading-6 text-slate-600">{step.description}</p>
              </div>
            </li>
          ))}
        </ol>
      </Card>

      <Card>
        <h2 className="text-lg font-semibold text-slate-900">Migration path</h2>
        <ul className="mt-4 list-disc space-y-2 pl-5 text-sm leading-6 text-slate-700">
          {report.migration_path.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </Card>

      <Card>
        <h2 className="text-lg font-semibold text-slate-900">Tradeoffs and risks</h2>
        <ul className="mt-4 list-disc space-y-2 pl-5 text-sm leading-6 text-slate-700">
          {report.tradeoffs.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </Card>

      {report.alternatives.length > 0 ? (
        <Card>
          <h2 className="text-lg font-semibold text-slate-900">Alternatives</h2>
          <div className="mt-4 space-y-3">
            {report.alternatives.map((alt) => (
              <div key={alt.tool_id} className="rounded-lg border border-slate-200 px-4 py-3">
                <p className="font-medium text-slate-900">{alt.name}</p>
                <p className="mt-1 text-sm text-slate-600">{alt.choose_if}</p>
              </div>
            ))}
          </div>
        </Card>
      ) : null}
    </div>
  );
}
