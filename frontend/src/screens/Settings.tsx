import { useState, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Check,
  Database,
  Monitor,
  Moon,
  RefreshCw,
  Save,
  ShieldCheck,
  Sun,
  Trash2,
} from "lucide-react";
import { api, post } from "../api";
import { useWorkspace } from "../state";
import type { Session, Settings } from "../types";
import {
  Button,
  Confirm,
  ErrorNotice,
  Field,
  Loading,
  Notice,
  PageHeading,
  Panel,
} from "../components/ui";

export default function SettingsScreen() {
  const settings = useQuery({
    queryKey: ["settings"],
    queryFn: () => api<Settings>("/settings"),
  });
  return (
    <>
      <PageHeading
        eyebrow="LOCAL PREFERENCES"
        title="Settings"
        description="Control session lifetimes, indexing boundaries, and how this workspace behaves."
      />
      <ErrorNotice
        error={settings.error}
        onRetry={() => {
          void settings.refetch();
        }}
      />
      {settings.isLoading && <Loading />}
      {settings.data && <SettingsForm initial={settings.data} />}
    </>
  );
}

function SettingsForm({ initial }: { initial: Settings }) {
  const client = useQueryClient();
  const { session, refresh } = useWorkspace();
  const [draft, setDraft] = useState(initial);
  const [ignored, setIgnored] = useState(
    initial.ignored_directories.join("\n"),
  );
  const [deleting, setDeleting] = useState<Session | null>(null);
  const [saved, setSaved] = useState(false);
  const update = useMutation({
    mutationFn: () =>
      api<Settings>("/settings", {
        method: "PUT",
        body: JSON.stringify({
          ...draft,
          ignored_directories: ignored
            .split("\n")
            .map((value) => value.trim())
            .filter(Boolean),
        }),
      }),
    onSuccess: async (result) => {
      client.setQueryData(["settings"], result);
      setDraft(result);
      setIgnored(result.ignored_directories.join("\n"));
      setSaved(true);
      await refresh();
    },
  });
  const cleanup = useMutation({
    mutationFn: () => post<Record<string, unknown>>("/cleanup"),
    onSuccess: refresh,
  });
  const clear = useMutation({
    mutationFn: (target: Session) => post(`/sessions/${target.id}/clear`),
    onSuccess: async (_result, target) => {
      setDeleting(null);
      client.removeQueries({ predicate: (query) =>
        (query.queryKey[0] === "memories" && query.queryKey[1] === target.id) ||
        (query.queryKey[0] === "passport" && query.queryKey[2] === target.id),
      });
      await refresh();
    },
  });
  const diagnostics = useQuery({
    queryKey: ["diagnostics"],
    queryFn: () => api<Record<string, unknown>>("/diagnostics"),
    enabled: false,
  });
  function change<K extends keyof Settings>(key: K, value: Settings[K]) {
    setDraft((previous) => ({ ...previous, [key]: value }));
    setSaved(false);
  }
  function submit(event: FormEvent) {
    event.preventDefault();
    update.mutate();
  }
  const dirty =
    JSON.stringify(draft) !== JSON.stringify(initial) ||
    ignored !== initial.ignored_directories.join("\n");
  return (
    <>
      <form className="settings-form" onSubmit={submit}>
        <Panel
          title="Session & context"
          subtitle="Temporary memory should last for the task, not forever."
        >
          <div className="settings-fields">
            <Field
              label="Inactivity timeout (minutes)"
              htmlFor="setting-ttl"
              hint="Only meaningful session activity refreshes this timer."
            >
              <input
                id="setting-ttl"
                type="number"
                min={1}
                max={480}
                required
                value={draft.session_ttl_minutes}
                onChange={(event) =>
                  change("session_ttl_minutes", Number(event.target.value))
                }
              />
            </Field>
            <Field
              label="Maximum lifetime (hours)"
              htmlFor="setting-lifetime"
              hint="An absolute limit, even for an active session."
            >
              <input
                id="setting-lifetime"
                type="number"
                min={1}
                max={168}
                required
                value={draft.max_session_hours}
                onChange={(event) =>
                  change("max_session_hours", Number(event.target.value))
                }
              />
            </Field>
            <Field
              label="Default context token budget"
              htmlFor="setting-budget"
              hint="Estimated response tokens including metadata; expand explicitly when more context is needed."
            >
              <input
                id="setting-budget"
                type="number"
                min={256}
                max={100000}
                required
                value={draft.context_token_budget}
                onChange={(event) =>
                  change("context_token_budget", Number(event.target.value))
                }
              />
            </Field>
          </div>
        </Panel>
        <Panel
          title="Repository indexing"
          subtitle="Default security exclusions always apply in addition to these preferences."
        >
          <div className="settings-fields">
            <Field
              label="Ignored directories"
              htmlFor="setting-ignored"
              hint="One directory name per line, without path separators. Reindex existing projects after changing exclusions."
            >
              <textarea
                id="setting-ignored"
                rows={4}
                value={ignored}
                onChange={(event) => {
                  setIgnored(event.target.value);
                  setSaved(false);
                }}
                placeholder="coverage\n.generated"
                spellCheck={false}
              />
            </Field>
            <Field
              label="Maximum indexed file size (bytes)"
              htmlFor="setting-size"
              hint="Files exceeding this limit are skipped. Reindex projects after changing this limit."
            >
              <input
                id="setting-size"
                type="number"
                min={1024}
                max={5000000}
                required
                value={draft.max_file_size}
                onChange={(event) =>
                  change("max_file_size", Number(event.target.value))
                }
              />
            </Field>
          </div>
          <Toggle
            label="Watch for file changes"
            description="Update the local index and invalidate stale source references when repository files change."
            checked={draft.watch_enabled}
            onChange={(value) => change("watch_enabled", value)}
          />
          <Toggle
            label="Record local events"
            description="Store indexing, retrieval, and memory activity in the local SQLite timeline."
            checked={draft.event_logging}
            onChange={(value) => change("event_logging", value)}
          />
        </Panel>
        <Panel
          title="Appearance"
          subtitle="Choose a theme for this local dashboard."
        >
          <div
            className="theme-options"
            role="group"
            aria-label="Theme preference"
          >
            <button
              type="button"
              aria-pressed={draft.theme === "dark"}
              className={draft.theme === "dark" ? "selected" : ""}
              onClick={() => change("theme", "dark")}
            >
              <Moon size={20} />
              <span>Dark</span>
              {draft.theme === "dark" && <Check size={15} />}
            </button>
            <button
              type="button"
              aria-pressed={draft.theme === "light"}
              className={draft.theme === "light" ? "selected" : ""}
              onClick={() => change("theme", "light")}
            >
              <Sun size={20} />
              <span>Light</span>
              {draft.theme === "light" && <Check size={15} />}
            </button>
            <button
              type="button"
              aria-pressed={draft.theme === "system"}
              className={draft.theme === "system" ? "selected" : ""}
              onClick={() => change("theme", "system")}
            >
              <Monitor size={20} />
              <span>System</span>
              {draft.theme === "system" && <Check size={15} />}
            </button>
          </div>
        </Panel>
        <ErrorNotice error={update.error} />
        {saved && (
          <div role="status" className="inline-success">
            <Check size={15} />
            Settings saved to the local service.
          </div>
        )}
        <div className="settings-save">
          <p>
            {dirty
              ? "You have unsaved changes."
              : "Preferences are stored on this machine."}
          </p>
          <Button type="submit" busy={update.isPending} disabled={!dirty}>
            <Save size={16} />
            Save settings
          </Button>
        </div>
      </form>
      <Panel
        title="Local data & maintenance"
        subtitle="You control the persistent index and temporary task memory."
        className="maintenance-panel"
      >
        <div className="maintenance-row">
          <Database size={19} />
          <div className="grow">
            <strong>Clean up expired sessions</strong>
            <p>Remove expired sessions and their associated task data now.</p>
          </div>
          <Button
            variant="secondary"
            busy={cleanup.isPending}
            onClick={() => cleanup.mutate()}
          >
            <RefreshCw size={14} />
            Run cleanup
          </Button>
        </div>
        {cleanup.isSuccess && (
          <div role="status" className="inline-success">
            <Check size={14} />
            Cleanup complete. <code>{JSON.stringify(cleanup.data)}</code>
          </div>
        )}
        <ErrorNotice error={cleanup.error} />
        <div className="maintenance-row">
          <Trash2 size={19} />
          <div className="grow">
            <strong>Delete selected session</strong>
            <p>
              {session
                ? `Permanently remove “${session.task}” and all of its memories, retrievals, and events.`
                : "Select a session in the workspace bar to delete its task data."}
            </p>
          </div>
          <Button
            variant="danger"
            disabled={!session}
            onClick={() => {
              clear.reset();
              if (session) setDeleting(session);
            }}
          >
            Delete session data
          </Button>
        </div>
        <div className="maintenance-row">
          <ShieldCheck size={19} />
          <div className="grow">
            <strong>Local diagnostics</strong>
            <p>
              Inspect service health, storage, and integration configuration.
            </p>
          </div>
          <Button
            variant="secondary"
            busy={diagnostics.isFetching}
            onClick={() => {
              void diagnostics.refetch();
            }}
          >
            Run diagnostics
          </Button>
        </div>
        <ErrorNotice error={diagnostics.error} />
        {diagnostics.data && (
          <pre className="detail-json">
            {JSON.stringify(diagnostics.data, null, 2)}
          </pre>
        )}
      </Panel>
      <Notice tone="neutral">
        Memglide stores data locally. It does not send repository contents to a
        Memglide cloud service. Deleting task data never deletes source code.
      </Notice>
      {deleting && (
        <Confirm
          title="Delete all data for this session?"
          description={`This permanently removes “${deleting.task}”, its memories, retrievals, Context Passports, and session events.`}
          confirmLabel="Delete session data"
          busy={clear.isPending}
          error={clear.error}
          onConfirm={() => clear.mutate(deleting)}
          onClose={() => setDeleting(null)}
        />
      )}
    </>
  );
}

function Toggle({
  label,
  description,
  checked,
  onChange,
}: {
  label: string;
  description: string;
  checked: boolean;
  onChange: (value: boolean) => void;
}) {
  return (
    <label className="setting-toggle">
      <span>
        <strong>{label}</strong>
        <p>{description}</p>
      </span>
      <input
        className="toggle-input"
        type="checkbox"
        role="switch"
        checked={checked}
        onChange={(event) => onChange(event.target.checked)}
        aria-label={label}
      />
    </label>
  );
}
