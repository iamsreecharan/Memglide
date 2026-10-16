import { useEffect, useState, type FormEvent } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  BrainCircuit,
  Check,
  FileCode2,
  Pencil,
  Plus,
  Search,
  ShieldAlert,
  Trash2,
} from "lucide-react";
import { api, list, post, queryString } from "../api";
import { dateTime, readable, relative } from "../format";
import { useWorkspace } from "../state";
import type { Memory } from "../types";
import {
  Badge,
  Button,
  Confirm,
  Empty,
  ErrorNotice,
  Field,
  Loading,
  Modal,
  Notice,
  PageHeading,
  Panel,
  RouteLink,
} from "../components/ui";

const categories = [
  "observation",
  "decision",
  "error",
  "failed_attempt",
  "verified_fix",
  "open_issue",
  "checkpoint",
];

export default function MemoryScreen() {
  const { sessionId, session, projectId, refresh } = useWorkspace();
  const [search, setSearch] = useState("");
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const [editing, setEditing] = useState<Memory | "new" | null>(null);
  const [deleting, setDeleting] = useState<Memory | null>(null);
  useEffect(() => {
    const timeout = window.setTimeout(() => setQuery(search), 250);
    return () => window.clearTimeout(timeout);
  }, [search]);
  const memories = useQuery({
    queryKey: ["memories", sessionId, query, category],
    queryFn: async () =>
      list(
        await api<Memory[] | Record<string, Memory[]>>(
          `/sessions/${sessionId}/memories${queryString({ query, category })}`,
        ),
        "memories",
      ),
    enabled: Boolean(sessionId && !session?.ended_at),
    refetchOnWindowFocus: false,
  });
  const remove = useMutation({
    mutationFn: () =>
      api(`/sessions/${sessionId}/memories/${deleting?.id}`, {
        method: "DELETE",
      }),
    onSuccess: async () => {
      setDeleting(null);
      await refresh();
    },
  });
  const invalidate = useMutation({
    mutationFn: (id: string) =>
      post(`/sessions/${sessionId}/memories/${id}/invalidate`),
    onSuccess: refresh,
  });
  const canWrite = Boolean(sessionId && !session?.ended_at);
  return (
    <>
      <PageHeading
        eyebrow="TEMPORARY TASK KNOWLEDGE"
        title="Memory explorer"
        description="Explicit findings, decisions, and fixes. Every memory has a source and an expiration."
        actions={
          <Button disabled={!canWrite} onClick={() => setEditing("new")}>
            <Plus size={16} />
            Save a memory
          </Button>
        }
      />
      {!projectId ? (
        <Panel>
          <Empty
            icon={BrainCircuit}
            title="Choose a project first"
            description="Register a repository, then start a session to keep meaningful task knowledge."
            action={<RouteLink to="/projects">Open projects</RouteLink>}
          />
        </Panel>
      ) : !sessionId ? (
        <Panel>
          <Empty
            icon={BrainCircuit}
            title="A session gives memory a home"
            description="Start or select a session in the workspace bar. Session memories expire automatically after inactivity."
          />
        </Panel>
      ) : session?.ended_at ? (
        <Panel>
          <Empty
            icon={BrainCircuit}
            title="This session has ended"
            description="Select an active session to explore memory. You can still delete this session's task data or inspect its project timeline."
            action={<RouteLink to="/timeline">Open project timeline</RouteLink>}
          />
        </Panel>
      ) : (
        <>
          <div className="filter-bar">
            <div className="search-input">
              <Search size={17} />
              <input
                aria-label="Search memories"
                placeholder="Search findings, errors, decisions…"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
              />
            </div>
            <div className="filter-count">
              {memories.data?.length ?? "—"} memories
            </div>
          </div>
          <div
            className="category-tabs"
            role="group"
            aria-label="Memory categories"
          >
            <button
              className={!category ? "selected" : ""}
              onClick={() => setCategory("")}
            >
              All memories
            </button>
            {categories.map((item) => (
              <button
                key={item}
                className={category === item ? "selected" : ""}
                onClick={() => setCategory(item)}
              >
                {readable(item)}
              </button>
            ))}
          </div>
          {session?.ended_at && (
            <Notice tone="neutral">
              This session has ended. Its records are retained locally until
              expiration or deletion. Select an active session to explore
              memory.
            </Notice>
          )}
          <ErrorNotice
            error={memories.error}
            onRetry={() => {
              void memories.refetch();
            }}
          />
          <ErrorNotice error={invalidate.error} />
          {memories.isLoading ? (
            <Loading label="Reading session memories…" />
          ) : !memories.data?.length && !memories.error ? (
            <Panel>
              <Empty
                icon={BrainCircuit}
                title={
                  query || category ? "No matching memories" : "A fresh session"
                }
                description={
                  query || category
                    ? "Try another search or category. You can review all memories by clearing the filters."
                    : "Save observations and verified findings as you work. Memglide never captures hidden agent reasoning."
                }
                action={
                  query || category ? (
                    <Button
                      variant="secondary"
                      onClick={() => {
                        setSearch("");
                        setCategory("");
                      }}
                    >
                      Clear filters
                    </Button>
                  ) : canWrite ? (
                    <Button onClick={() => setEditing("new")}>
                      <Plus size={15} />
                      Save a memory
                    </Button>
                  ) : undefined
                }
              />
            </Panel>
          ) : (
            <div className="memory-grid">
              {memories.data?.map((memory) => (
                <Panel key={memory.id} className="memory-card">
                  <div className="memory-top">
                    <Badge>{readable(memory.category)}</Badge>
                    <Badge
                      tone={
                        memory.stale ||
                        memory.freshness === "Requires inspection"
                          ? "amber"
                          : "green"
                      }
                    >
                      {memory.freshness ?? (memory.stale ? "Stale" : "Current")}
                    </Badge>
                    <span className="grow" />
                    <Button
                      variant="ghost"
                      aria-label={`Edit memory ${memory.content.slice(0, 24)}`}
                      disabled={!canWrite}
                      onClick={() => setEditing(memory)}
                    >
                      <Pencil size={15} />
                    </Button>
                    <Button
                      variant="ghost"
                      aria-label={`Delete memory ${memory.content.slice(0, 24)}`}
                      onClick={() => {
                        remove.reset();
                        setDeleting(memory);
                      }}
                    >
                      <Trash2 size={15} />
                    </Button>
                  </div>
                  <p className="memory-content">{memory.content}</p>
                  <div className="memory-provenance">
                    <span>PROVENANCE</span>
                    <p>{memory.provenance}</p>
                  </div>
                  {memory.sources.length > 0 && (
                    <div className="memory-sources">
                      {memory.sources.map((source) => (
                        <div key={source.path}>
                          <FileCode2 size={13} />
                          <code>{source.path}</code>
                          <span title={`Source hash: ${source.hash}`}>
                            {source.hash.slice(0, 8)}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="memory-footer">
                    <time title={dateTime(memory.updated_at)}>
                      {relative(memory.updated_at)}
                    </time>
                    <span>Expires with session</span>
                    {!memory.stale && canWrite && (
                      <Button
                        variant="ghost"
                        busy={
                          invalidate.isPending &&
                          invalidate.variables === memory.id
                        }
                        onClick={() => invalidate.mutate(memory.id)}
                      >
                        <ShieldAlert size={13} />
                        Mark stale
                      </Button>
                    )}
                  </div>
                </Panel>
              ))}
            </div>
          )}
        </>
      )}
      {editing && (
        <MemoryEditor
          memory={editing === "new" ? null : editing}
          onClose={() => setEditing(null)}
        />
      )}
      {deleting && (
        <Confirm
          title="Delete this memory?"
          description="This immediately removes the finding and its source references from this session."
          confirmLabel="Delete memory"
          busy={remove.isPending}
          error={remove.error}
          onConfirm={() => remove.mutate()}
          onClose={() => setDeleting(null)}
        />
      )}
    </>
  );
}

function MemoryEditor({
  memory,
  onClose,
}: {
  memory: Memory | null;
  onClose: () => void;
}) {
  const { sessionId, refresh } = useWorkspace();
  const [content, setContent] = useState(memory?.content ?? "");
  const [category, setCategory] = useState(memory?.category ?? "observation");
  const [provenance, setProvenance] = useState(
    memory?.provenance ?? "User submitted through the local dashboard",
  );
  const [sources, setSources] = useState("");
  const save = useMutation({
    mutationFn: () =>
      memory
        ? api(`/sessions/${sessionId}/memories/${memory.id}`, {
            method: "PATCH",
            body: JSON.stringify({
              content: content.trim(),
              provenance: provenance.trim(),
            }),
          })
        : post(`/sessions/${sessionId}/memories`, {
            category,
            content: content.trim(),
            provenance: provenance.trim(),
            sources: sources
              .split("\n")
              .map((path) => path.trim())
              .filter(Boolean)
              .map((path) => ({ path })),
          }),
    onSuccess: async () => {
      await refresh();
      onClose();
    },
  });
  function submit(event: FormEvent) {
    event.preventDefault();
    save.mutate();
  }
  return (
    <Modal
      title={memory ? "Edit memory" : "Save a memory"}
      description="Record useful task knowledge explicitly. Code references are checked against current source hashes."
      onClose={onClose}
    >
      <form onSubmit={submit}>
        <div className="form-stack">
          <Field label="Category" htmlFor="memory-category">
            <select
              id="memory-category"
              value={category}
              disabled={Boolean(memory)}
              onChange={(event) => setCategory(event.target.value)}
            >
              {categories.map((item) => (
                <option key={item} value={item}>
                  {readable(item)}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Finding" htmlFor="memory-content">
            <textarea
              id="memory-content"
              value={content}
              onChange={(event) => setContent(event.target.value)}
              required
              rows={5}
              maxLength={32000}
              placeholder="What did you learn or verify?"
            />
          </Field>
          <Field
            label="Provenance"
            htmlFor="memory-provenance"
            hint="How was this finding established? Include an observation, command, or source."
          >
            <textarea
              id="memory-provenance"
              value={provenance}
              onChange={(event) => setProvenance(event.target.value)}
              required
              rows={2}
              maxLength={4000}
            />
          </Field>
          {!memory && (
            <Field
              label="Related files (optional)"
              htmlFor="memory-sources"
              hint="One project-relative path per line. The backend records the current file hash."
            >
              <textarea
                id="memory-sources"
                value={sources}
                onChange={(event) => setSources(event.target.value)}
                rows={2}
                placeholder="src/auth.py"
                spellCheck={false}
              />
            </Field>
          )}
          <ErrorNotice error={save.error} />
        </div>
        <div className="modal-actions">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button
            type="submit"
            busy={save.isPending}
            disabled={!content.trim() || !provenance.trim()}
          >
            <Check size={15} />
            {memory ? "Save changes" : "Save memory"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
