import { useEffect, useState, type FormEvent } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  ArrowDown,
  ArrowRight,
  ChevronRight,
  Compass,
  Fingerprint,
  Search,
  ShieldCheck,
} from "lucide-react";
import { Link, useSearchParams } from "react-router-dom";
import { api, post } from "../api";
import { dateTime } from "../format";
import { useWorkspace } from "../state";
import type { Passport, Retrieval, Settings } from "../types";
import {
  Badge,
  Button,
  Empty,
  ErrorNotice,
  Field,
  Notice,
  PageHeading,
  Panel,
  RouteLink,
} from "../components/ui";
import { DependencyList, EvidenceCard } from "../components/Evidence";

const levels = [
  { value: 1, title: "Discovery", detail: "Symbols & locations" },
  {
    value: 2,
    title: "Focused",
    detail: "Implementations & direct dependencies",
  },
  { value: 3, title: "Expanded", detail: "Modules, callers & related tests" },
];

export default function ContextScreen() {
  const {
    projectId,
    sessionId,
    session,
    retrieval: lastRetrieval,
    setRetrieval,
    refresh,
  } = useWorkspace();
  const [params] = useSearchParams();
  const retrieval =
    lastRetrieval?.session_id === sessionId ? lastRetrieval : null;
  const [query, setQuery] = useState(retrieval?.query ?? "");
  const [level, setLevel] = useState(retrieval?.level ?? 1);
  const [budget, setBudget] = useState<number | "">(retrieval?.budget ?? "");
  useEffect(() => {
    const question = params.get("query");
    if (question) setQuery(question);
  }, [params]);
  const settings = useQuery({
    queryKey: ["settings"],
    queryFn: () => api<Settings>("/settings"),
  });
  const currentPassport = useQuery({
    queryKey: ["passport", retrieval?.retrieval_id ?? "", sessionId],
    queryFn: () =>
      api<Passport>(
        `/context/${retrieval?.retrieval_id}/passport?session_id=${encodeURIComponent(sessionId)}`,
      ),
    enabled: Boolean(retrieval && sessionId && !session?.ended_at),
    refetchInterval: 15000,
    retry: false,
  });
  const activeBudget = budget || settings.data?.context_token_budget || 4000;
  const retrieve = useMutation({
    mutationFn: () =>
      post<Retrieval>("/context", {
        session_id: sessionId,
        query: query.trim(),
        level,
        budget: activeBudget,
      }),
    onSuccess: async (result) => {
      setRetrieval(result);
      await refresh();
    },
  });
  const expand = useMutation({
    mutationFn: () =>
      post<Retrieval>(`/context/${retrieval?.retrieval_id}/expand`, {
        session_id: sessionId,
        level: Math.min(3, (retrieval?.level ?? 1) + 1),
        budget: activeBudget,
      }),
    onSuccess: async (result) => {
      setRetrieval(result);
      setLevel(result.level);
      await refresh();
    },
  });
  function submit(event: FormEvent) {
    event.preventDefault();
    retrieve.mutate();
  }
  const canRetrieve = Boolean(sessionId && !session?.ended_at);
  const busy = retrieve.isPending || expand.isPending;
  const staleFiles =
    (currentPassport.data?.stale_files as string[] | undefined) ?? [];
  return (
    <>
      <PageHeading
        eyebrow="SELECT → VERIFY → EXPAND"
        title="Context explorer"
        description="Ask a code question. Retrieve ranked source evidence within a transparent token budget."
      />
      {!projectId && (
        <Notice tone="neutral">
          Register a repository in{" "}
          <Link to="/projects" className="inline-link">
            Projects
          </Link>{" "}
          to begin.
        </Notice>
      )}
      {projectId && !sessionId && (
        <Notice tone="neutral">
          Start or select a session above to retrieve context for your task.
        </Notice>
      )}
      {session?.ended_at && (
        <Notice>
          This session has ended. Start a new session to retrieve current
          context.
        </Notice>
      )}
      <Panel className="context-query-panel">
        <form onSubmit={submit}>
          <label className="eyebrow" htmlFor="context-question">
            WHAT DO YOU NEED TO UNDERSTAND?
          </label>
          <div className="context-search">
            <Search size={21} />
            <textarea
              id="context-question"
              rows={2}
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              required
              maxLength={5000}
              placeholder="Where is authentication handled, and what depends on it?"
              onKeyDown={(event) => {
                if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
                  event.preventDefault();
                  if (canRetrieve && query.trim() && !busy) retrieve.mutate();
                }
              }}
            />
          </div>
          <div className="context-query-bottom">
            <div
              className="level-picker"
              role="group"
              aria-label="Retrieval depth"
            >
              {levels.map((item) => (
                <button
                  type="button"
                  key={item.value}
                  className={level === item.value ? "selected" : ""}
                  title={item.detail}
                  aria-pressed={level === item.value}
                  onClick={() => setLevel(item.value)}
                >
                  <span>L{item.value}</span>
                  {item.title}
                </button>
              ))}
            </div>
            <Field label="Token budget" htmlFor="context-budget">
              <input
                id="context-budget"
                type="number"
                min={256}
                max={100000}
                step={1}
                value={budget}
                placeholder={String(
                  settings.data?.context_token_budget ?? 4000,
                )}
                onChange={(event) =>
                  setBudget(
                    event.target.value === "" ? "" : Number(event.target.value),
                  )
                }
              />
            </Field>
            <Button
              type="submit"
              busy={retrieve.isPending}
              disabled={!canRetrieve || !query.trim() || expand.isPending}
            >
              Retrieve context
              <ArrowRight size={16} />
            </Button>
          </div>
        </form>
      </Panel>
      <ErrorNotice error={retrieve.error || expand.error} />
      {retrieval ? (
        <>
          <div className="results-heading">
            <div>
              <span className="eyebrow">RETRIEVAL SNAPSHOT</span>
              <h2>{retrieval.query}</h2>
              <p>
                {retrieval.items.length} evidence items <span>·</span> Level{" "}
                {retrieval.level} <span>·</span> {retrieval.memories.length}{" "}
                relevant memories
              </p>
            </div>
            <Link
              className="button button-secondary"
              to={`/passport?retrieval=${encodeURIComponent(retrieval.retrieval_id)}&session=${encodeURIComponent(sessionId)}`}
            >
              <Fingerprint size={16} />
              View passport
              <ChevronRight size={14} />
            </Link>
          </div>
          <ErrorNotice error={currentPassport.error} />
          {staleFiles.length > 0 && (
            <Notice title="Source changed since retrieval">
              {staleFiles.map((path) => (
                <p key={path}>
                  <code>{path}</code> no longer matches this evidence. Retrieve
                  again to select updated source.
                </p>
              ))}
            </Notice>
          )}
          {retrieval.warnings.length > 0 && (
            <Notice
              title={
                retrieval.truncated
                  ? "Context is partial"
                  : "Inspect before relying on this context"
              }
            >
              {retrieval.warnings.map((warning, index) => (
                <p key={index}>{warning}</p>
              ))}
            </Notice>
          )}
          <div className="context-results">
            <div className="stack">
              {retrieval.items.length ? (
                retrieval.items.map((item, index) => (
                  <EvidenceCard
                    key={`${item.path}-${item.symbol ?? item.name ?? ""}-${index}`}
                    item={{
                      ...item,
                      freshness: staleFiles.includes(item.path)
                        ? "Stale"
                        : item.freshness === "Current"
                          ? "Current at retrieval"
                          : item.freshness,
                    }}
                    rank={index + 1}
                  />
                ))
              ) : (
                <Panel>
                  <Empty
                    icon={Search}
                    title="No source evidence matched"
                    description="Try a specific symbol, file path, or identifier. No context was fabricated for this query."
                  />
                </Panel>
              )}
              {retrieval.session_events && (
                <Panel
                  title="Source changes since session start"
                  subtitle={retrieval.session_event_scope}
                >
                  <div className="dependency-list">
                    {retrieval.session_events.map((event) => (
                      <div key={event.id} className="dependency-row">
                        <div className="grow">
                          <code>{event.path}</code>
                          <p>{dateTime(event.created_at)}</p>
                        </div>
                        <Badge tone={event.deleted ? "amber" : "neutral"}>
                          {event.deleted ? "Deleted" : "Changed"}
                        </Badge>
                      </div>
                    ))}
                  </div>
                  {!retrieval.session_events.length && (
                    <p className="section-empty">
                      No source-change events recorded since this session
                      started.
                    </p>
                  )}
                </Panel>
              )}
              {retrieval.memories.length > 0 && (
                <Panel title="Relevant session memory">
                  <div className="retrieved-memories">
                    {retrieval.memories.map((memory) => (
                      <div key={memory.id}>
                        <Badge>{memory.category.replace(/_/g, " ")}</Badge>
                        <p>{memory.content}</p>
                        <span>{memory.provenance}</span>
                      </div>
                    ))}
                  </div>
                </Panel>
              )}
              {retrieval.dependencies.length > 0 && (
                <Panel title="Related dependencies">
                  <DependencyList items={retrieval.dependencies} />
                </Panel>
              )}
            </div>
            <div className="stack">
              <Panel title="Context budget" className="budget-panel">
                <div className="budget-total">
                  {retrieval.estimated_tokens.toLocaleString()}
                  <span> / {retrieval.budget.toLocaleString()}</span>
                </div>
                <p>estimated tokens returned</p>
                <div className="budget-track">
                  <span
                    style={{
                      width: `${Math.min(100, (retrieval.estimated_tokens / Math.max(1, retrieval.budget)) * 100)}%`,
                    }}
                  />
                </div>
                <div className="budget-status">
                  <span>
                    {retrieval.truncated
                      ? "Partial selection"
                      : "Within budget"}
                  </span>
                  <Badge tone={retrieval.truncated ? "amber" : "green"}>
                    {retrieval.truncated ? "Review" : "Selected"}
                  </Badge>
                </div>
                <p className="field-hint">
                  {retrieval.token_estimate_method ??
                    "Estimated locally across the complete response, including metadata. Actual model tokenization may differ."}
                </p>
              </Panel>
              <Panel title="Progressive evidence">
                <div className="depth-steps">
                  {levels.map((item) => (
                    <div
                      key={item.value}
                      className={item.value <= retrieval.level ? "reached" : ""}
                    >
                      <span>{item.value}</span>
                      <div>
                        <strong>{item.title}</strong>
                        <p>{item.detail}</p>
                      </div>
                    </div>
                  ))}
                </div>
                {retrieval.level < 3 ? (
                  <Button
                    variant="secondary"
                    className="full-width"
                    busy={expand.isPending}
                    disabled={!canRetrieve || retrieve.isPending}
                    onClick={() => expand.mutate()}
                  >
                    <ArrowDown size={15} />
                    Expand to level {retrieval.level + 1}
                  </Button>
                ) : (
                  <p className="field-hint">
                    Maximum depth selected. Inspect full-source references when
                    further evidence is needed.
                  </p>
                )}
              </Panel>
              <div className="context-assurance">
                <ShieldCheck size={19} />
                <p>
                  Current source wins.
                  <br />A passport documents evidence and gaps; it cannot prove
                  completeness.
                </p>
              </div>
            </div>
          </div>
        </>
      ) : (
        <Panel className="context-empty">
          <Empty
            icon={Compass}
            title="Start with a question"
            description="Exact symbols, file paths, and natural language queries help Memglide find relevant local evidence. Begin with discovery, then expand when needed."
          />
          <div className="context-example">
            <span>TRY A QUESTION</span>
            <button
              onClick={() => setQuery("Where is authentication handled?")}
            >
              Where is authentication handled?
              <ArrowRight size={14} />
            </button>
            <button
              onClick={() => setQuery("What files depend on this module?")}
            >
              What files depend on this module?
              <ArrowRight size={14} />
            </button>
          </div>
          <RouteLink to="/passport">Understand Context Passports</RouteLink>
        </Panel>
      )}
    </>
  );
}
