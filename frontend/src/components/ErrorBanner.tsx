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
    <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
      {message}
    </div>
  );
}
