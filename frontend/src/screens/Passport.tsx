import { useEffect, useRef, useState, type FormEvent } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowRight,
  Check,
  FileCheck2,
  Fingerprint,
  GitFork,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
} from "lucide-react";
import { Link, useSearchParams } from "react-router-dom";
import { api, queryString } from "../api";
import { describe } from "../format";
import { useWorkspace } from "../state";
import type { Overview, Passport } from "../types";
import {
  Badge,
  Button,
  Empty,
  ErrorNotice,
  Field,
  Loading,
  Notice,
  PageHeading,
  Panel,
  RouteLink,
} from "../components/ui";
import { DependencyList, EvidenceList } from "../components/Evidence";

export default function PassportScreen() {
  const {
    retrieval,
    projectId,
    sessionId,
    session,
    sessions,
    sessionsLoading,
    selectProject,
    selectSession,
  } = useWorkspace();
  const [params, setParams] = useSearchParams();
  const overview = useQuery({
    queryKey: ["overview"],
    queryFn: () => api<Overview>("/overview"),
  });
  const retrievalId =
    params.get("retrieval") ??
    (retrieval?.session_id === sessionId ? retrieval?.retrieval_id : "") ??
    "";
  const passportSession =
    params.get("session") ??
    (retrievalId === retrieval?.retrieval_id
      ? retrieval.session_id
      : sessionId);
  const alignedSession = useRef("");
  useEffect(() => {
    if (!params.get("session")) {
      alignedSession.current = "";
      return;
    }
    if (alignedSession.current === passportSession) return;
    const target = overview.data?.sessions.find(
      (item) => item.id === passportSession,
    );
    if (target) {
      if (target.project_id !== projectId) {
        selectProject(target.project_id);
      } else if (
        !sessionsLoading &&
        sessions.some((item) => item.id === target.id)
      ) {
        if (target.id !== sessionId) selectSession(target.id);
        else alignedSession.current = passportSession;
      }
    }
  }, [
    overview.data,
    passportSession,
    projectId,
    sessionId,
    sessions,
    sessionsLoading,
    params,
    selectProject,
    selectSession,
  ]);
  const isEnded =
    (session?.id === passportSession && Boolean(session?.ended_at)) ||
    (overview.data?.sessions.some(
      (item) => item.id === passportSession && Boolean(item.ended_at),
    ) ??
      false);
  const [manualId, setManualId] = useState(retrievalId);
  useEffect(() => {
    setManualId(retrievalId);
  }, [retrievalId]);
  const passport = useQuery({
    queryKey: ["passport", retrievalId, passportSession],
    queryFn: () =>
      api<Passport>(
        `/context/${encodeURIComponent(retrievalId)}/passport${queryString({ session_id: passportSession })}`,
      ),
    enabled: Boolean(retrievalId && passportSession && !isEnded),
    refetchOnWindowFocus: false,
  });
  function select(id: string) {
    const record = overview.data?.recent_retrievals.find(
      (item) => item.id === id,
    );
    if (id)
      setParams({ retrieval: id, session: record?.session_id ?? sessionId });
    else setParams({});
  }
  function submit(event: FormEvent) {
    event.preventDefault();
    select(manualId.trim());
  }
  const data = isEnded || passport.error ? undefined : passport.data;
  const dependencies = data?.dependencies ?? data?.relevant_dependencies ?? [];
  const unresolved = data?.unresolved_dependencies ?? [];
  const missing = [
    ...(data?.missing_context ?? data?.missing_context_indicators ?? []),
    ...(data?.warnings ?? []),
  ];
  const hashes = data?.verified_source_hashes ?? {};
  const hashEntries = Array.isArray(hashes)
    ? hashes.map((item) => [describe(item.path), describe(item.hash)] as const)
    : Object.entries(hashes);
  const next = data?.recommended_next_retrievals ?? [];
  const freshness =
    typeof data?.source_freshness === "string"
      ? data.source_freshness
      : "Requires inspection";
  const current = data?.status === "Current" && freshness === "Current";
  return (
    <>
      <PageHeading
        eyebrow="THE EVIDENCE RECORD"
        title="Context passport"
        description="See what was selected, which source versions were verified, and what still needs inspection."
        actions={
          retrievalId && (
            <Button
              variant="secondary"
              disabled={isEnded}
              busy={passport.isFetching}
              onClick={() => {
                void passport.refetch();
              }}
            >
              <RefreshCw size={15} />
              Verify source versions
            </Button>
          )
        }
      />
      <Panel className="passport-selector">
        <Field label="Recent retrieval" htmlFor="passport-retrieval">
          <select
            id="passport-retrieval"
            value={
              overview.data?.recent_retrievals.some(
                (item) => item.id === retrievalId,
              )
                ? retrievalId
                : ""
            }
            onChange={(event) => select(event.target.value)}
          >
            <option value="">Choose a retrieval</option>
            {overview.data?.recent_retrievals.map((item) => (
              <option key={item.id} value={item.id}>
                {item.query} · L{item.level}
              </option>
            ))}
          </select>
        </Field>
        <form onSubmit={submit}>
          <Field label="Or open by retrieval ID" htmlFor="passport-id">
            <div className="inline-field">
              <input
                id="passport-id"
                value={manualId}
                onChange={(event) => setManualId(event.target.value)}
                placeholder="Retrieval identifier"
                autoComplete="off"
                spellCheck={false}
              />
              <Button
                variant="secondary"
                type="submit"
                disabled={!manualId.trim() || !sessionId}
              >
                Open
              </Button>
            </div>
          </Field>
        </form>
      </Panel>
      {isEnded && (
        <Notice>
          This session has ended. Its project timeline records remain until
          cleanup; retrieve new context in an active session.
        </Notice>
      )}
      <ErrorNotice
        error={isEnded ? null : passport.error}
        onRetry={() => {
          void passport.refetch();
        }}
      />
      {passport.isLoading && <Loading label="Verifying source evidence…" />}
      {!retrievalId && (
        <Panel>
          <Empty
            icon={Fingerprint}
            title="Every retrieval gets a passport"
            description="Retrieve context in a session to inspect its evidence, source freshness, dependency gaps, and recommended next steps."
            action={
              <Link to="/context" className="button button-primary">
                Retrieve your first context
                <ArrowRight size={15} />
              </Link>
            }
          />
        </Panel>
      )}
      {data && (
        <>
          <section
            className={`passport-banner ${current ? "passport-current" : "passport-partial"}`}
          >
            <div className="passport-seal">
              {current ? (
                <ShieldCheck size={34} strokeWidth={1.3} />
              ) : (
                <ShieldAlert size={34} strokeWidth={1.3} />
              )}
            </div>
            <div className="grow">
              <div className="eyebrow">
                CONTEXT PASSPORT <span>/</span>{" "}
                {String(data.retrieval_id ?? retrievalId).slice(0, 12)}
              </div>
              <h2>{data.status ?? "Requires inspection"} evidence</h2>
              <p>
                {data.evidence_quality ?? "Evidence quality requires review."}
              </p>
            </div>
            <div className="passport-banner-meta">
              <Badge tone={freshness === "Current" ? "green" : "amber"}>
                {freshness} sources
              </Badge>
              <span>
                {(
                  data.estimated_tokens_returned ??
                  data.estimated_tokens ??
                  0
                ).toLocaleString()}{" "}
                / {(data.token_budget ?? data.budget ?? 0).toLocaleString()}{" "}
                est. tokens
              </span>
            </div>
          </section>
          <div className="passport-stats">
            <div>
              <FileCheck2 size={17} />
              <strong>{data.selected_files?.length ?? 0}</strong>
              <span>selected files</span>
            </div>
            <div>
              <Fingerprint size={17} />
              <strong>{data.selected_symbols?.length ?? 0}</strong>
              <span>selected symbols</span>
            </div>
            <div>
              <GitFork size={17} />
              <strong>
                {dependencies.filter((item) => item.resolved).length}
              </strong>
              <span>resolved dependencies</span>
            </div>
            <div>
              <ShieldAlert size={17} />
              <strong>{unresolved.length}</strong>
              <span>unresolved relationships</span>
            </div>
          </div>
          {(missing.length > 0 ||
            (data.stale_files as string[] | undefined)?.length) && (
            <Notice title="More inspection may be needed">
              {missing.map((warning, index) => (
                <p key={index}>{warning}</p>
              ))}
              {(data.stale_files as string[] | undefined)?.map((path) => (
                <p key={path}>
                  Source changed: <code>{path}</code>
                </p>
              ))}
            </Notice>
          )}
          <div className="passport-columns">
            <div className="stack">
              <Panel
                title="Selected source evidence"
                subtitle="File locations and symbols included in this retrieval."
              >
                <div className="passport-section">
                  <h3>Files</h3>
                  <EvidenceList
                    items={data.selected_files ?? []}
                    empty="No files selected."
                  />
                </div>
                <div className="passport-section">
                  <h3>Symbols</h3>
                  <EvidenceList
                    items={(data.selected_symbols ?? []).map((item) =>
                      typeof item === "string"
                        ? item
                        : `${String(item.path ?? "")}:${String(item.start_line ?? "")} ${String(item.symbol ?? item.name ?? "")}`,
                    )}
                    empty="No symbols selected."
                  />
                </div>
              </Panel>
              <Panel
                title="Verified source versions"
                subtitle="SHA-256 hashes bind this evidence to the indexed file contents."
              >
                {hashEntries.length ? (
                  <div className="hash-list">
                    {hashEntries.map(([path, hash]) => (
                      <div key={path}>
                        <Check size={14} />
                        <code>{path}</code>
                        <code title={hash}>{hash.slice(0, 16)}…</code>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="section-empty">
                    No verified source hashes returned.
                  </p>
                )}
              </Panel>
              <Panel title="Dependencies covered">
                {dependencies.length ? (
                  <DependencyList items={dependencies} />
                ) : (
                  <p className="section-empty">
                    No dependency relationships were returned.
                  </p>
                )}
              </Panel>
            </div>
            <div className="stack">
              <Panel
                title="Unresolved relationships"
                action={
                  <Badge tone={unresolved.length ? "amber" : "neutral"}>
                    {unresolved.length}
                  </Badge>
                }
              >
                {unresolved.length ? (
                  <DependencyList items={unresolved} />
                ) : (
                  <p className="section-empty">
                    No unresolved relationships reported. This does not
                    establish completeness.
                  </p>
                )}
              </Panel>
              <Panel
                title="Related tests"
                subtitle="Discovered from repository structure; no tests were executed."
              >
                <EvidenceList
                  items={data.related_tests ?? []}
                  empty="No related tests discovered. Inspect test coverage before making a change."
                />
              </Panel>
              <Panel title="Suggested next inspections">
                {next.length ? (
                  <div className="next-inspections">
                    {next.map((item, index) => (
                      <Link
                        key={index}
                        to={`/context?query=${encodeURIComponent(describe(item))}`}
                      >
                        <span>{index + 1}</span>
                        <p>{describe(item)}</p>
                        <ArrowRight size={14} />
                      </Link>
                    ))}
                  </div>
                ) : (
                  <p className="section-empty">
                    No additional retrievals recommended.
                  </p>
                )}
              </Panel>
            </div>
          </div>
          <Notice tone="neutral" title="Evidence is a guide, not a proof">
            A Context Passport records what Memglide found and verified. Static
            analysis cannot guarantee that every dependency or necessary detail
            has been included.
          </Notice>
        </>
      )}
      {!data && retrievalId && !passport.isLoading && !passport.error && (
        <RouteLink to="/context">Return to context explorer</RouteLink>
      )}
    </>
  );
}
