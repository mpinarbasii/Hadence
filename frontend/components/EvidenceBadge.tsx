/**
 * Renders an assessment level (see backend app/domain/value_objects.py ->
 * AssessmentLevel) as a small, calm badge — never a bare numeric score.
 * Deliberately text-first: the label carries the meaning, color is a
 * secondary cue only (see docs/architecture.md §"UX / Design direction").
 */

export type AssessmentLevel = "strong" | "partial" | "weak" | "none" | "conflicting";

const LABELS: Record<AssessmentLevel, string> = {
  strong: "Strong evidence",
  partial: "Partial evidence",
  weak: "Weak evidence",
  none: "No evidence found",
  conflicting: "Conflicting evidence",
};

const STYLES: Record<AssessmentLevel, string> = {
  strong: "bg-evidence-strong/10 text-evidence-strong border-evidence-strong/30",
  partial: "bg-evidence-partial/10 text-evidence-partial border-evidence-partial/30",
  weak: "bg-evidence-weak/10 text-evidence-weak border-evidence-weak/30",
  none: "bg-evidence-none/10 text-evidence-none border-evidence-none/30",
  conflicting: "bg-evidence-weak/10 text-evidence-weak border-evidence-weak/30",
};

export function EvidenceBadge({ level }: { level: AssessmentLevel }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${STYLES[level]}`}
    >
      {LABELS[level]}
    </span>
  );
}
