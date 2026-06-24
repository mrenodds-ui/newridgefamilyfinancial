import type { FinancialSourceReviewItem } from "../../api/client";

function confidenceBadgeClass(label: string, reviewRequired: boolean) {
  if (label === "manual review") {
    return "dashboard-import-status-badge dashboard-import-status-badge--error";
  }
  if (reviewRequired || label === "review suggested") {
    return "dashboard-import-status-badge dashboard-import-status-badge--pending";
  }
  return "dashboard-import-status-badge";
}

function humanizeMetricKey(key: string) {
  return key
    .replace(/([a-z0-9])([A-Z])/g, "$1 $2")
    .replaceAll("_", " ")
    .toLowerCase();
}

function humanizeLabel(value: string) {
  return value.replaceAll("_", " ");
}

function humanizeConfidenceLabel(value: string) {
  if (value === "manual review") {
    return "needs review";
  }
  return humanizeLabel(value);
}

type SourceReviewContentProps = {
  review?: FinancialSourceReviewItem | null;
  emptyMessage: string;
};

export function SourceReviewContent({ review, emptyMessage }: SourceReviewContentProps) {
  if (!review) {
    return <div className="hal-answer-card">{emptyMessage}</div>;
  }

  const metricEntries = Object.entries(review.metrics ?? {}).filter(([, value]) => value !== null && value !== undefined);
  const reviewFlags = review.reviewFlags ?? [];

  return (
    <div className="admin-audit-item">
      <div className="admin-audit-item__header">
        <strong>{review.sourceSystem}</strong>
        <span>
          {humanizeLabel(review.status)} ·{" "}
          <span className={confidenceBadgeClass(review.confidenceLabel, review.reviewRequired)}>{humanizeConfidenceLabel(review.confidenceLabel)}</span>
        </span>
      </div>
      <div className="admin-audit-item__summary">{review.summary}</div>
      <div className="admin-audit-item__summary">Last checked: {review.lastVerifiedAt ?? "Unavailable"}</div>
      {metricEntries.length ? (
        <div className="admin-audit-item__summary">
          {metricEntries.map(([key, value]) => `${humanizeMetricKey(key)}: ${value}`).join(" · ")}
        </div>
      ) : null}
      <div className="admin-audit-item__summary">
        {reviewFlags.length ? (
          reviewFlags.map((flag) => (
            <span
              key={`${review.sourceSystem}-${flag}`}
              className="dashboard-import-status-badge dashboard-import-status-badge--pending dashboard-import-status-badge--spaced"
            >
              {humanizeLabel(flag)}
            </span>
          ))
        ) : (
          <span className="dashboard-import-status-badge">no follow-up flags</span>
        )}
      </div>
    </div>
  );
}
