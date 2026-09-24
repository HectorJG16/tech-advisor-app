import Link from "next/link";

interface AppShellProps {
  children: React.ReactNode;
  subtitle?: string;
}

export function AppShell({ children, subtitle }: AppShellProps) {
  return (
    <div className="min-h-full bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <div>
            <Link href="/" className="text-lg font-semibold tracking-tight text-slate-900">
              Tech Advisor
            </Link>
            {subtitle ? <p className="mt-1 text-sm text-slate-500">{subtitle}</p> : null}
          </div>
          <span className="rounded-full bg-teal-50 px-3 py-1 text-xs font-medium text-teal-700">
            AI automation advisor
          </span>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-6 py-10">{children}</main>
    </div>
  );
}
