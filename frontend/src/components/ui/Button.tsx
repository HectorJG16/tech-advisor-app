import type { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost";
}

export function Button({
  variant = "primary",
  className = "",
  disabled,
  ...props
}: ButtonProps) {
  const base =
    "inline-flex items-center justify-center rounded-xl px-5 py-2.5 text-sm font-semibold transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-50 disabled:shadow-none";
  const styles =
    variant === "primary"
      ? "bg-gradient-to-r from-cyan-400 via-indigo-400 to-violet-400 text-zinc-950 shadow-[0_0_28px_rgba(34,211,238,0.35)] hover:scale-[1.02] hover:shadow-[0_0_36px_rgba(129,140,248,0.45)] active:scale-[0.98]"
      : variant === "secondary"
        ? "border border-white/12 bg-white/5 text-zinc-100 backdrop-blur-sm hover:border-white/20 hover:bg-white/10 hover:shadow-[0_0_20px_rgba(255,255,255,0.06)]"
        : "text-zinc-400 hover:bg-white/5 hover:text-zinc-200";

  return (
    <button
      className={`${base} ${styles} ${className}`}
      disabled={disabled}
      {...props}
    />
  );
}
