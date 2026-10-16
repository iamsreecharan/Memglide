import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  ArrowRight,
  ArrowUpRight,
  Database,
  FileCode2,
  Fingerprint,
  FolderGit2,
  GitBranch,
  Layers3,
  Radio,
  ShieldCheck,
  Terminal,
} from "lucide-react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { bytes, dateTime, describe, readable, relative } from "../format";
import { useWorkspace } from "../state";
import type { Overview } from "../types";
import {
  Badge,
  Empty,
  ErrorNotice,
  Loading,
  Notice,
  PageHeading,
  Panel,
  RouteLink,
} from "../components/ui";

export default function OverviewScreen() {
  const { selectProject, selectSession } = useWorkspace();
  const overview = useQuery({
    queryKey: ["overview"],
    queryFn: () => api<Overview>("/overview"),
    refetchInterval: 15000,
  });
  const data = overview.data;
  const activeSessions =
    data?.sessions.filter((session) => !session.ended_at) ?? [];
  return (
    <>
      <PageHeading
        eyebrow="YOUR LOCAL WORKSPACE"
        title="Your context, in focus."
        description="Remember what matters. Retrieve what's needed. Verify what's missing."
        actions={
          <Link className="button button-secondary" to="/context">
            <CompassIcon />
            Explore context
            <ArrowUpRight size={15} />
          </Link>
        }
      />
      <ErrorNotice
        error={overview.error}
        onRetry={() => {
          void overview.refetch();
        }}
      />
      {overview.isLoading && <Loading />}
      {data && (
        <>
          <div className="metric-grid">
            <Metric
              icon={FolderGit2}
              label="Registered projects"
              value={data.counts.projects}
              note="Approved local repositories"
              to="/projects"
            />
            <Metric
              icon={FileCode2}
              label="Indexed files"
              value={data.counts.files}
              note={`${data.counts.symbols.toLocaleString()} structural symbols`}
              to="/projects"
            />
            <Metric
              icon={Layers3}
              label="Active sessions"
              value={activeSessions.length}
              note="Temporary task workspaces"
              to="/timeline"
            />
            <Metric
              icon={Database}
              label="Session memories"
              value={data.counts.memories}
              note={`${bytes(data.counts.database_bytes)} local database`}
              to="/memory"
            />
          </div>
          {data.warnings.length > 0 && (
            <Notice title="Needs your attention">
              {data.warnings.map((warning, index) => (
                <p key={index}>{warning}</p>
              ))}
            </Notice>
          )}
          <div className="overview-columns">
            <div className="stack">
              <Panel
                title="Your projects"
                subtitle="Source code is the authority. The index follows."
                action={<RouteLink to="/projects">Manage projects</RouteLink>}
              >
                {!data.projects.length ? (
                  <Empty
                    icon={FolderGit2}
                    title="Start with a repository"
                    description="Register a local project to index its files, symbols, and relationships."
                    action={
                      <Link className="button button-primary" to="/projects">
                        Add your first project
                        <ArrowRight size={15} />
                      </Link>
                    }
                  />
                ) : (
                  <div className="project-list">
                    {data.projects.map((project) => (
                      <Link
                        key={project.id}
                        to="/projects"
                        className="project-row"
                        onClick={() => selectProject(project.id)}
                      >
                        <span className="project-icon">
                          <FolderGit2 size={21} strokeWidth={1.5} />
                        </span>
                        <div className="grow">
                          <strong>{project.name}</strong>
                          <p className="path-text">{project.path}</p>
                        </div>
                        <div className="project-row-meta">
                          <span>
                            <GitBranch size={12} />
                            {project.branch ?? "No Git branch"}
                          </span>
                          <span>
                            {(
                              project.index_stats.file_count ?? 0
                            ).toLocaleString()}{" "}
                            files
                          </span>
                        </div>
                        <span className="project-status">
                          <span
                            className={`status-dot ${project.indexed_at ? "" : "dot-wait"}`}
                          />
                          {project.indexed_at ? "Indexed" : "Not indexed"}
                        </span>
                        <ArrowUpRight className="muted" size={16} />
                      </Link>
                    ))}
                  </div>
                )}
              </Panel>
              <Panel
                title="Recent retrievals"
                subtitle="Evidence selected for your latest questions."
                action={<RouteLink to="/context">Open explorer</RouteLink>}
              >
                {!data.recent_retrievals.length ? (
                  <Empty
                    icon={Fingerprint}
                    title="No retrievals yet"
                    description="Start a session and ask a code question to build your first Context Passport."
                  />
                ) : (
                  <div className="retrieval-list">
                    {data.recent_retrievals.map((retrieval) => (
                      <Link
                        key={retrieval.id}
                        className="retrieval-row"
                        to={`/passport?retrieval=${encodeURIComponent(retrieval.id)}&session=${encodeURIComponent(retrieval.session_id)}`}
                        onClick={() => {
                          selectProject(retrieval.project_id);
                          selectSession(retrieval.session_id);
                        }}
                      >
                        <span className="retrieval-icon">
                          <Fingerprint size={17} />
                        </span>
                        <div className="grow">
                          <strong>{retrieval.query}</strong>
                          <p>
                            Level {retrieval.level} <span>·</span>{" "}
                            {retrieval.estimated_tokens.toLocaleString()}{" "}
                            estimated tokens <span>·</span>{" "}
                            {relative(retrieval.created_at)}
                          </p>
                        </div>
                        <ArrowUpRight size={15} className="muted" />
                      </Link>
                    ))}
                  </div>
                )}
              </Panel>
            </div>
            <div className="stack">
              <Panel title="System status" className="system-panel">
                <div className="status-row">
                  <span className="status-icon">
                    <Radio size={17} />
                  </span>
                  <div className="grow">
                    <strong>Local API</strong>
                    <p>Running on your machine</p>
                  </div>
                  <Badge tone="green">Connected</Badge>
                </div>
                <div className="status-row">
                  <span className="status-icon">
                    <Terminal size={17} />
                  </span>
                  <div className="grow">
                    <strong>Codex MCP</strong>
                    <p>{data.mcp.detail}</p>
                  </div>
                </div>
                <div className="system-foot">
                  <ShieldCheck size={15} />
                  <span>No remote telemetry. No cloud database.</span>
                </div>
              </Panel>
              <Panel
                title="Active sessions"
                action={
                  <span className="count-label">{activeSessions.length}</span>
                }
              >
                {!activeSessions.length ? (
                  <Empty
                    icon={Layers3}
                    title="No active sessions"
                    description="Select a project above and start a session for your next task."
                  />
                ) : (
                  <div className="active-sessions">
                    {activeSessions.slice(0, 5).map((session) => (
                      <button
                        key={session.id}
                        className="session-row"
                        onClick={() => {
                          selectProject(session.project_id);
                          selectSession(session.id);
                        }}
                      >
                        <span className="status-dot" />
                        <div className="grow">
                          <strong>{session.task}</strong>
                          <p title={dateTime(session.expires_at)}>
                            Expires {relative(session.expires_at)}
                          </p>
                        </div>
                        <ArrowRight size={14} />
                      </button>
                    ))}
                  </div>
                )}
              </Panel>
              <Panel
                title="Indexing & activity"
                action={<RouteLink to="/timeline">View all</RouteLink>}
              >
                {!data.recent_events.length ? (
                  <Empty
                    icon={Activity}
                    title="A clean timeline"
                    description="Indexing, retrieval, and memory events will appear here."
                  />
                ) : (
                  <div className="compact-events">
                    {data.recent_events.slice(0, 5).map((event) => (
                      <div key={event.id} className="compact-event">
                        <span className="event-dot" />
                        <div className="grow">
                          <strong>{readable(event.type)}</strong>
                          <p title={JSON.stringify(event.detail)}>
                            {describe(
                              event.detail.query ??
                                event.detail.path ??
                                event.detail.task ??
                                "",
                            )}
                          </p>
                        </div>
                        <time title={dateTime(event.created_at)}>
                          {relative(event.created_at)}
                        </time>
                      </div>
                    ))}
                  </div>
                )}
              </Panel>
            </div>
          </div>
          <div className="principle-bar">
            <span className="principle-icon">
              <ShieldCheck size={18} />
            </span>
            <div>
              <strong>Evidence over assumptions.</strong>
              <p>
                A smaller response is useful context, not a claim of total model
                token savings.
              </p>
            </div>
            <Link to="/passport">
              Inspect the evidence
              <ArrowRight size={14} />
            </Link>
          </div>
        </>
      )}
    </>
  );
}

function CompassIcon() {
  return <Fingerprint size={16} />;
}

function Metric({
  icon: Icon,
  label,
  value,
  note,
  to,
}: {
  icon: typeof FolderGit2;
  label: string;
  value: number;
  note: string;
  to: string;
}) {
  return (
    <Link to={to} className="metric-card">
      <div className="metric-top">
        <span>{label}</span>
        <Icon size={17} strokeWidth={1.5} />
      </div>
      <div className="metric-value">{value.toLocaleString()}</div>
      <div className="metric-note">
        {note}
        <ArrowUpRight size={13} />
      </div>
    </Link>
  );
}
