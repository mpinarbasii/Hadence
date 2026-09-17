import { EvidenceBadge } from "@/components/EvidenceBadge";

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center px-6 py-24">
      <p className="text-sm font-medium uppercase tracking-wide text-muted">
        Application Intelligence Workspace
      </p>
      <h1 className="mt-3 text-4xl font-semibold tracking-tight text-ink sm:text-5xl">
        Your career, backed by evidence.
      </h1>
      <p className="mt-6 max-w-xl text-lg text-muted">
        Hadence builds a persistent Career Evidence Graph from your real
        history, then uses it to show exactly what a job actually requires —
        and what you can genuinely prove.
      </p>

      <div className="mt-10 flex flex-col gap-3 rounded-lg border border-black/10 bg-white p-5">
        <p className="text-sm font-medium text-ink">Example requirement mapping</p>
        <div className="flex items-center justify-between border-b border-black/5 pb-3">
          <span className="text-sm text-ink">Python</span>
          <EvidenceBadge level="strong" />
        </div>
        <div className="flex items-center justify-between border-b border-black/5 pb-3">
          <span className="text-sm text-ink">SQL</span>
          <EvidenceBadge level="partial" />
        </div>
        <div className="flex items-center justify-between">
          <span className="text-sm text-ink">Power BI</span>
          <EvidenceBadge level="none" />
        </div>
      </div>

      <p className="mt-10 text-sm text-muted">
        This is a foundation-stage build. See{" "}
        <code className="rounded bg-black/5 px-1 py-0.5">docs/architecture.md</code> and{" "}
        <code className="rounded bg-black/5 px-1 py-0.5">docs/domain-model.md</code> in the repo
        for the roadmap.
      </p>
    </main>
  );
}
