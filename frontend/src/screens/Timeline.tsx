import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Activity, ChevronDown, RefreshCw } from "lucide-react";
import { api, list, queryString } from "../api";
import { dateTime, describe, readable } from "../format";
import { useWorkspace } from "../state";
import type { Event } from "../types";
import {
  Badge,
  Button,
  Empty,
  ErrorNotice,
  Field,
  Loading,
  PageHeading,
  Panel,
  RouteLink,
} from "../components/ui";

export default function TimelineScreen() {
  const { projectId, sessionId, session, project } = useWorkspace();
  const [eventType, setEventType] = useState("");
  const [onlySession, setOnlySession] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);
  const events = useQuery({
    queryKey: [
      "events",
      projectId,
      onlySession && !session?.ended_at ? sessionId : "",
    ],
    queryFn: async () =>
      list(
        await api<Event[] | Record<string, Event[]>>(
          `/events${queryString({ project_id: projectId, session_id: onlySession && !session?.ended_at ? sessionId : undefined })}`,
        ),
        "events",
      ),
    enabled: Boolean(projectId),
    refetchInterval: 15000,
  });
  const types = [
    ...new Set((events.data ?? []).map((event) => event.type)),
  ].sort();
  const filtered = (events.data ?? []).filter(
    (event) => !eventType || event.type === eventType,
  );
  return (
    <>
      <PageHeading
        eyebrow="A TRACEABLE WORKFLOW"
        title="Session timeline"
        description="Indexing, retrieval, and memory activity recorded locally as it happens."
        actions={
          <Button
            variant="secondary"
            disabled={!projectId}
            busy={events.isFetching}
            onClick={() => {
              void events.refetch();
            }}
          >
            <RefreshCw size={15} />
            Refresh events
          </Button>
        }
      />
      {!projectId ? (
        <Panel>
          <Empty
            icon={Activity}
            title="No project selected"
            description="Register a repository to begin recording local activity."
            action={<RouteLink to="/projects">Open projects</RouteLink>}
          />
        </Panel>
      ) : (
        <>
          <div className="timeline-filters">
            <Field label="Event type" htmlFor="event-type">
              <select
                id="event-type"
                value={eventType}
                onChange={(event) => setEventType(event.target.value)}
              >
                <option value="">All event types</option>
                {types.map((type) => (
                  <option key={type} value={type}>
                    {readable(type)}
                  </option>
                ))}
              </select>
            </Field>
            <label className="check-label">
              <input
                type="checkbox"
                checked={onlySession && !session?.ended_at}
                disabled={!sessionId || Boolean(session?.ended_at)}
                onChange={(event) => setOnlySession(event.target.checked)}
              />
              Selected session only
            </label>
            <span className="filter-count">
              {filtered.length} events in {project?.name}
            </span>
          </div>
          <ErrorNotice
            error={events.error}
            onRetry={() => {
              void events.refetch();
            }}
          />
          {events.isLoading ? (
            <Loading label="Loading recorded events…" />
          ) : !filtered.length && !events.error ? (
            <Panel>
              <Empty
                icon={Activity}
                title={
                  eventType
                    ? "No events match this filter"
                    : "No recorded events yet"
                }
                description="Add a project, index source code, retrieve context, and save memories to build a traceable timeline."
              />
            </Panel>
          ) : (
            <Panel className="timeline-panel">
              <ol className="timeline-list">
                {filtered.map((event) => (
                  <li
                    key={event.id}
                    className={`timeline-event ${event.type.includes("invalid") || event.type.includes("changed") ? "event-warning" : ""}`}
                  >
                    <div className="timeline-marker">
                      <span />
                    </div>
                    <div className="timeline-body">
                      <div className="timeline-title">
                        <strong>{readable(event.type)}</strong>
                        <time
                          dateTime={new Date(
                            typeof event.created_at === "number"
                              ? event.created_at * 1000
                              : event.created_at,
                          ).toISOString()}
                        >
                          {dateTime(event.created_at)}
                        </time>
                      </div>
                      <p>
                        {describe(
                          event.detail.query ??
                            event.detail.task ??
                            event.detail.path ??
                            event.detail.content ??
                            event.detail.message ??
                            event.detail.project_name ??
                            event.detail.name ??
                            "",
                        )}
                      </p>
                      <div className="timeline-meta">
                        {event.session_id && (
                          <Badge>Session {event.session_id.slice(0, 8)}</Badge>
                        )}
                        <Button
                          variant="ghost"
                          aria-expanded={expanded === event.id}
                          onClick={() =>
                            setExpanded(expanded === event.id ? null : event.id)
                          }
                        >
                          Event details
                          <ChevronDown size={13} />
                        </Button>
                      </div>
                      {expanded === event.id && (
                        <pre className="detail-json">
                          {JSON.stringify(event.detail, null, 2)}
                        </pre>
                      )}
                    </div>
                  </li>
                ))}
              </ol>
            </Panel>
          )}
        </>
      )}
    </>
  );
}
