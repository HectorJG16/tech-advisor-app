import { ReportFlow } from "@/components/ReportFlow";

interface ReportPageProps {
  params: Promise<{ id: string }>;
}

export default async function ReportPage({ params }: ReportPageProps) {
  const { id } = await params;
  return <ReportFlow sessionId={id} />;
}
