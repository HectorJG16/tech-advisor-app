"use client";

import { motion } from "motion/react";
import type { ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  delay?: number;
}

export function Card({ children, className = "", hover = false, delay = 0 }: CardProps) {
  return (
    <motion.section
      className={`gradient-border relative overflow-hidden rounded-2xl p-6 shadow-[0_8px_32px_rgba(0,0,0,0.35)] ${hover ? "transition-transform duration-300 hover:-translate-y-1 hover:shadow-[0_16px_48px_rgba(34,211,238,0.12)]" : ""} ${className}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: [0.22, 1, 0.36, 1] }}
    >
      <div
        className="pointer-events-none absolute inset-0 bg-gradient-to-br from-white/[0.06] via-transparent to-transparent"
        aria-hidden
      />
      <div className="relative">{children}</div>
    </motion.section>
  );
}
