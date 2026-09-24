import Link from "next/link";

interface AppShellProps {
  children: React.ReactNode;
  subtitle?: string;
}

export function AppShell({ children, subtitle }: AppShellProps) {
  return (
    <div className="relative min-h-full overflow-hidden bg-[#050508] text-zinc-100">
      <div className="pointer-events-none fixed inset-0 grid-overlay opacity-60" aria-hidden />
      <div className="ambient-orb ambient-orb-1" aria-hidden />
      <div className="ambient-orb ambient-orb-2" aria-hidden />
      <div className="ambient-orb ambient-orb-3" aria-hidden />

      <header className="sticky top-0 z-20 border-b border-white/8 bg-[#050508]/70 backdrop-blur-xl">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <div>
            <Link
              href="/"
              className="text-lg font-semibold tracking-tight transition-opacity hover:opacity-80"
            >
              <span className="gradient-text">Tech Advisor</span>
            </Link>
            {subtitle ? (
              <p className="mt-1 text-sm text-zinc-400">{subtitle}</p>
            ) : null}
          </div>
          <span className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-xs font-medium text-cyan-300 shadow-[0_0_20px_rgba(34,211,238,0.15)]">
            AI automation advisor
          </span>
        </div>
      </header>

      <main className="relative z-10 mx-auto max-w-5xl px-6 py-10">{children}</main>
    </div>
  );
}
