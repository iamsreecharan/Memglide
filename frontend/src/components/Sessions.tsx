import { useState, type FormEvent } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Clock3, CircleStop, Plus, Trash2 } from "lucide-react";
import { api, post } from "../api";
import { dateTime, relative } from "../format";
import { useWorkspace } from "../state";
import type { Session } from "../types";
import { Badge, Button, Confirm, ErrorNotice, Field, Modal } from "./ui";

export default function Sessions() {
  const client = useQueryClient();
  const {
    projectId,
    sessionId,
    project,
    session,
    projects,
    sessions,
    selectProject,
    selectSession,
    refresh,
    projectsLoading,
    sessionsLoading,
    sessionsError,
  } = useWorkspace();
  const [create, setCreate] = useState(false);
  const [task, setTask] = useState("");
  const [confirm, setConfirm] = useState<"end" | "delete" | null>(null);
  const start = useMutation({
    mutationFn: () =>
      post<Session>("/sessions", { project_id: projectId, task: task.trim() }),
    onSuccess: async (result) => {
      await refresh();
      selectSession(result.id);
      setCreate(false);
      setTask("");
    },
  });
  const end = useMutation({
    mutationFn: () =>
      api<Session>(`/sessions/${sessionId}`, { method: "DELETE" }),
    onSuccess: async (ended) => {
      client.setQueryData<Session[]>(["sessions", projectId], (previous) =>
        previous?.map((item) => (item.id === ended.id ? ended : item)),
      );
      client.removeQueries({
        predicate: (query) =>
          (query.queryKey[0] === "memories" &&
            query.queryKey[1] === ended.id) ||
          (query.queryKey[0] === "passport" && query.queryKey[2] === ended.id),
      });
      setConfirm(null);
      await Promise.all([
        client.invalidateQueries({ queryKey: ["sessions", projectId] }),
        client.invalidateQueries({ queryKey: ["overview"] }),
        client.invalidateQueries({ queryKey: ["events"] }),
      ]);
    },
  });
  const clear = useMutation({
    mutationFn: () => post(`/sessions/${sessionId}/clear`),
    onSuccess: async () => {
      setConfirm(null);
      selectSession("");
      await refresh();
    },
  });
  function submit(event: FormEvent) {
    event.preventDefault();
    start.mutate();
  }

  return (
    <>
      <div className="workspace-bar">
        <div className="workspace-pickers">
          <div className="workspace-picker">
            <label htmlFor="workspace-project">PROJECT</label>
            <select
              id="workspace-project"
              value={projectId}
              disabled={projectsLoading || !projects.length}
              onChange={(event) => selectProject(event.target.value)}
            >
              {!projects.length && (
                <option value="">No projects registered</option>
              )}
              {projects.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
          </div>
          <div className="picker-divider" />
          <div className="workspace-picker session-picker">
            <label htmlFor="workspace-session">SESSION</label>
            <select
              id="workspace-session"
              value={sessionId}
              disabled={!projectId || sessionsLoading}
              onChange={(event) => selectSession(event.target.value)}
            >
              <option
                value=""
                disabled={sessions.some((item) => !item.ended_at)}
              >
                Select a session
              </option>
              <optgroup label="Active sessions">
                {sessions
                  .filter((item) => !item.ended_at)
                  .map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.task}
                    </option>
                  ))}
              </optgroup>
              {sessions.some((item) => item.ended_at) && (
                <optgroup label="Ended sessions · deletion only">
                  {sessions
                    .filter((item) => item.ended_at)
                    .map((item) => (
                      <option key={item.id} value={item.id}>
                        {item.task} · ended
                      </option>
                    ))}
                </optgroup>
              )}
            </select>
          </div>
        </div>
        <div className="workspace-actions">
          {session && (
            <span
              className="session-expiry"
              title={`Expires ${dateTime(session.expires_at)}`}
            >
              <Clock3 size={13} />
              {session.ended_at ? (
                <Badge>Ended</Badge>
              ) : (
                `Expires ${relative(session.expires_at)}`
              )}
            </span>
          )}
          {session && !session.ended_at && (
            <Button
              variant="ghost"
              aria-label="End selected session"
              onClick={() => {
                end.reset();
                setConfirm("end");
              }}
            >
              <CircleStop size={16} />
            </Button>
          )}
          {session && (
            <Button
              variant="ghost"
              aria-label="Delete selected session and memory"
              onClick={() => {
                clear.reset();
                setConfirm("delete");
              }}
            >
              <Trash2 size={16} />
            </Button>
          )}
          <Button
            variant="secondary"
            disabled={!projectId}
            onClick={() => {
              start.reset();
              setCreate(true);
            }}
          >
            <Plus size={15} />
            <span>New session</span>
          </Button>
        </div>
      </div>
      {sessionsError && (
        <div className="bar-error">
          <ErrorNotice error={sessionsError} onRetry={refresh} />
        </div>
      )}
      {create && (
        <Modal
          title="Start a session"
          description={`Give your work in ${project?.name ?? "this project"} a clear task. Only meaningful activity refreshes expiration.`}
          onClose={() => setCreate(false)}
        >
          <form onSubmit={submit}>
            <Field label="Task" htmlFor="session-task">
              <input
                id="session-task"
                autoComplete="off"
                value={task}
                onChange={(event) => setTask(event.target.value)}
                required
                maxLength={2000}
                placeholder="Investigate authentication flow"
              />
            </Field>
            <ErrorNotice error={start.error} />
            <div className="modal-actions">
              <Button
                variant="secondary"
                type="button"
                onClick={() => setCreate(false)}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                busy={start.isPending}
                disabled={!task.trim()}
              >
                Start session
              </Button>
            </div>
          </form>
        </Modal>
      )}
      {confirm === "end" && (
        <Confirm
          title="End this session?"
          description="This stops activity in the session. Its records stay in local storage until expiration or manual deletion. Start another session to continue work."
          confirmLabel="End session"
          busy={end.isPending}
          error={end.error}
          onConfirm={() => end.mutate()}
          onClose={() => setConfirm(null)}
        />
      )}
      {confirm === "delete" && (
        <Confirm
          title="Delete session and memory?"
          description="This permanently removes the selected session, its memories, retrievals, passports, and events. Source code is never deleted."
          confirmLabel="Delete session"
          busy={clear.isPending}
          error={clear.error}
          onConfirm={() => clear.mutate()}
          onClose={() => setConfirm(null)}
        />
      )}
    </>
  );
}
