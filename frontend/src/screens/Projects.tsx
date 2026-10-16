import { useState, type FormEvent } from "react";
import { useMutation } from "@tanstack/react-query";
import {
  Check,
  ChevronDown,
  ChevronUp,
  FileCode2,
  FolderGit2,
  GitBranch,
  Plus,
  RefreshCw,
  Trash2,
} from "lucide-react";
import { api, post } from "../api";
import { dateTime, describe, relative } from "../format";
import { useWorkspace } from "../state";
import type { Project } from "../types";
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
} from "../components/ui";

export default function ProjectsScreen() {
  const {
    projects,
    projectId,
    selectProject,
    projectsLoading,
    projectsError,
    refresh,
  } = useWorkspace();
  const [adding, setAdding] = useState(false);
  const [path, setPath] = useState("");
  const add = useMutation({
    mutationFn: () => post<Project>("/projects", { path: path.trim() }),
    onSuccess: async (result) => {
      await refresh();
      selectProject(result.id);
      setAdding(false);
      setPath("");
    },
  });
  function submit(event: FormEvent) {
    event.preventDefault();
    add.mutate();
  }
  return (
    <>
      <PageHeading
        eyebrow="SOURCE INTELLIGENCE"
        title="Projects"
        description="Approve a local repository. Memglide indexes its structure without executing its code."
        actions={
          <Button
            onClick={() => {
              add.reset();
              setAdding(true);
            }}
          >
            <Plus size={16} />
            Add repository
          </Button>
        }
      />
      <ErrorNotice error={projectsError} onRetry={refresh} />
      {projectsLoading ? (
        <Loading />
      ) : !projects.length && !projectsError ? (
        <Panel>
          <Empty
            icon={FolderGit2}
            title="Your first project starts here"
            description="Add an absolute local repository path to discover files, symbols, and dependencies. Secrets and ignored files stay out of the index."
            action={
              <Button onClick={() => setAdding(true)}>
                <Plus size={16} />
                Add repository
              </Button>
            }
          />
        </Panel>
      ) : (
        <div className="project-cards">
          {projects.map((project) => (
            <ProjectCard
              key={project.id}
              project={project}
              selected={projectId === project.id}
              onSelect={() => selectProject(project.id)}
            />
          ))}
        </div>
      )}
      <div className="security-caption">
        <FolderGit2 size={15} />
        <p>
          Removing a registration deletes its local index and task data. It
          never deletes repository files.
        </p>
      </div>
      {adding && (
        <Modal
          title="Add a local repository"
          description="The directory must exist on the machine running Memglide. Registering it authorizes local indexing."
          onClose={() => setAdding(false)}
        >
          <form onSubmit={submit}>
            <Field
              label="Absolute repository path"
              htmlFor="project-path"
              hint="For example, /home/you/projects/my-app or C:\Users\you\projects\my-app."
            >
              <input
                id="project-path"
                value={path}
                onChange={(event) => setPath(event.target.value)}
                placeholder="/absolute/path/to/repository"
                required
                autoComplete="off"
                spellCheck={false}
              />
            </Field>
            <ErrorNotice error={add.error} />
            <div className="modal-actions">
              <Button
                type="button"
                variant="secondary"
                onClick={() => setAdding(false)}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                busy={add.isPending}
                disabled={!path.trim()}
              >
                Register & index
              </Button>
            </div>
          </form>
        </Modal>
      )}
    </>
  );
}

function ProjectCard({
  project,
  selected,
  onSelect,
}: {
  project: Project;
  selected: boolean;
  onSelect: () => void;
}) {
  const { refresh } = useWorkspace();
  const [expanded, setExpanded] = useState(false);
  const [full, setFull] = useState(false);
  const [removing, setRemoving] = useState(false);
  const reindex = useMutation({
    mutationFn: () => post(`/projects/${project.id}/reindex`, { full }),
    onSuccess: refresh,
  });
  const remove = useMutation({
    mutationFn: () => api(`/projects/${project.id}`, { method: "DELETE" }),
    onSuccess: async () => {
      setRemoving(false);
      await refresh();
    },
  });
  const stats = project.index_stats;
  const languages = Array.isArray(stats.languages)
    ? stats.languages.map((language) => [language, null] as const)
    : Object.entries(stats.languages ?? {});
  const ignored = Array.isArray(stats.ignored_files) ? stats.ignored_files : [];
  const errors = stats.errors ?? [];
  return (
    <Panel className={`project-card ${selected ? "selected-card" : ""}`}>
      <div className="project-card-top">
        <span className="project-icon">
          <FolderGit2 size={24} strokeWidth={1.5} />
        </span>
        <div className="grow">
          <h2>{project.name}</h2>
          <p className="path-text">{project.path}</p>
        </div>
        {selected ? (
          <Badge tone="green">
            <Check size={12} />
            Selected
          </Badge>
        ) : (
          <Button variant="secondary" onClick={onSelect}>
            Select project
          </Button>
        )}
      </div>
      <div className="project-facts">
        <div>
          <span>
            <GitBranch size={14} />
            Branch
          </span>
          <strong>{project.branch ?? "No Git repository"}</strong>
        </div>
        <div>
          <span>
            <FileCode2 size={14} />
            Indexed files
          </span>
          <strong>{(stats.file_count ?? 0).toLocaleString()}</strong>
        </div>
        <div>
          <span>Symbols</span>
          <strong>{(stats.symbol_count ?? 0).toLocaleString()}</strong>
        </div>
        <div>
          <span>Last indexed</span>
          <strong title={dateTime(project.indexed_at)}>
            {project.indexed_at ? relative(project.indexed_at) : "Not indexed"}
          </strong>
        </div>
      </div>
      <div className="project-card-bottom">
        <div className="language-tags">
          {languages.length ? (
            languages.map(([language, count]) => (
              <Badge key={language}>
                {language}
                {count !== null ? ` · ${count}` : ""}
              </Badge>
            ))
          ) : (
            <span className="muted">No indexed languages</span>
          )}
        </div>
        <div className="row-actions">
          <Button
            variant="ghost"
            aria-expanded={expanded}
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? "Hide details" : "Index details"}
            {expanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
          </Button>
          <Button
            variant="secondary"
            busy={reindex.isPending}
            onClick={() => reindex.mutate()}
          >
            <RefreshCw size={14} />
            Reindex
          </Button>
          <Button
            variant="ghost"
            aria-label={`Remove ${project.name}`}
            onClick={() => {
              remove.reset();
              setRemoving(true);
            }}
          >
            <Trash2 size={16} />
          </Button>
        </div>
      </div>
      <ErrorNotice error={reindex.error} />
      {reindex.isSuccess && (
        <div role="status" className="inline-success">
          <Check size={14} />
          Index updated from the current source.
        </div>
      )}
      {reindex.isPending && (
        <Notice tone="neutral">
          Indexing local files. This page will update when the operation
          completes.
        </Notice>
      )}
      {expanded && (
        <div className="project-details">
          <div>
            <h3>Indexing preferences</h3>
            <label className="check-label">
              <input
                type="checkbox"
                checked={full}
                onChange={(event) => setFull(event.target.checked)}
              />
              Force full reindex on next run
            </label>
            <p className="field-hint">
              Incremental indexing reuses unchanged file hashes by default.
            </p>
          </div>
          <div>
            <h3>Git working tree</h3>
            <pre className="detail-json">
              {JSON.stringify(project.git_state, null, 2)}
            </pre>
          </div>
          <div>
            <h3>
              Ignored files{" "}
              {typeof stats.ignored_files === "number"
                ? `(${stats.ignored_files})`
                : `(${ignored.length})`}
            </h3>
            {ignored.length > 0 ? (
              <ul className="file-list">
                {ignored.map((file, index) => (
                  <li key={index}>
                    <code>{typeof file === "string" ? file : file.path}</code>
                    {typeof file !== "string" && (
                      <p className="field-hint">{file.reason}</p>
                    )}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="muted">
                {typeof stats.ignored_files === "number"
                  ? "The index reported the count only."
                  : "No ignored file paths reported by this index."}
              </p>
            )}
          </div>
          <div>
            <h3>Index errors</h3>
            {errors.length > 0 ? (
              <ul className="warning-list">
                {errors.map((error, index) => (
                  <li key={index}>
                    {describe(error)}
                    {typeof error !== "string" && error.error
                      ? ` — ${String(error.error)}`
                      : ""}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="muted">No indexing errors reported.</p>
            )}
          </div>
        </div>
      )}
      {removing && (
        <Confirm
          title={`Remove ${project.name}?`}
          description="This removes the registration, persistent index, sessions, and associated task data. Your repository files stay on disk."
          confirmLabel="Remove project"
          busy={remove.isPending}
          error={remove.error}
          onConfirm={() => remove.mutate()}
          onClose={() => setRemoving(false)}
        />
      )}
    </Panel>
  );
}
