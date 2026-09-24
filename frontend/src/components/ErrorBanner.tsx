import { ApiError } from "@/lib/api";

interface ErrorBannerProps {
  error: unknown;
}

export function ErrorBanner({ error }: ErrorBannerProps) {
  let message = "Something went wrong. Please try again.";

  if (error instanceof ApiError) {
    if (error.status === 503) {
      message = "The recommendation engine is unavailable. Train the ranker and restart the API.";
    } else if (error.status === 409) {
      message = error.detail;
    } else {
      message = error.detail || message;
    }
  } else if (error instanceof Error) {
    message = error.message;
  }

  return (
    <div className="rounded-xl border border-red-400/25 bg-red-500/10 px-4 py-3 text-sm text-red-200 shadow-[0_0_24px_rgba(239,68,68,0.12)] backdrop-blur-sm">
      {message}
    </div>
  );
}
