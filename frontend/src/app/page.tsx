import { AppShell } from "@/components/AppShell";
import { ModeSelector } from "@/components/ModeSelector";

export default function Home() {
  return (
    <AppShell subtitle="Choose how you want to describe your scenario">
      <ModeSelector />
    </AppShell>
  );
}
