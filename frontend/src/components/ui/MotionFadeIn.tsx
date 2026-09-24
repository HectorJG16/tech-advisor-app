"use client";

import { motion } from "motion/react";
import type { ReactNode } from "react";

interface MotionFadeInProps {
  children: ReactNode;
  className?: string;
  delay?: number;
}

export function MotionFadeIn({ children, className = "", delay = 0 }: MotionFadeInProps) {
  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55, delay, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.div>
  );
}
