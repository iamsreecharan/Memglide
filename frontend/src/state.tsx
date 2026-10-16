import {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, list, queryString } from "./api";
import type { Project, Retrieval, Session, Settings } from "./types";

function stored(key: string): string {
  try {
    return localStorage.getItem(key) ?? "";
  } catch {
    return "";
  }
}
function persist(key: string, value: string): void {
  try {
    localStorage.setItem(key, value);
  } catch {
    /* Private browsing can disable storage. */
  }
}

interface WorkspaceState {
  projectId: string;
  sessionId: string;
  project: Project | undefined;
  session: Session | undefined;
  projects: Project[];
  sessions: Session[];
  projectsLoading: boolean;
  sessionsLoading: boolean;
  projectsError: Error | null;
  sessionsError: Error | null;
  selectProject: (id: string) => void;
  selectSession: (id: string) => void;
  refresh: () => Promise<void>;
  retrieval: Retrieval | null;
  setRetrieval: (retrieval: Retrieval | null) => void;
}

const WorkspaceContext = createContext<WorkspaceState | null>(null);

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const client = useQueryClient();
  const [projectId, setProjectId] = useState(() => stored("memglide.project"));
  const [sessionId, setSessionId] = useState(() => stored("memglide.session"));
  const [retrieval, updateRetrieval] = useState<Retrieval | null>(null);
  const activeSession = useRef(sessionId);
  const previousSession = useRef(sessionId);
  activeSession.current = sessionId;
  const projectsQuery = useQuery({
    queryKey: ["projects"],
    queryFn: async () =>
      list(
        await api<Project[] | Record<string, Project[]>>("/projects"),
        "projects",
      ),
    refetchInterval: 15000,
  });
  const sessionsQuery = useQuery({
    queryKey: ["sessions", projectId],
    queryFn: async () =>
      list(
        await api<Session[] | Record<string, Session[]>>(
          `/sessions${queryString({ project_id: projectId })}`,
        ),
        "sessions",
      ),
    enabled: Boolean(projectId),
    refetchInterval: 15000,
  });
  const settings = useQuery({
    queryKey: ["settings"],
    queryFn: () => api<Settings>("/settings"),
  });
  const projects = projectsQuery.data ?? [];
  const sessions = sessionsQuery.data ?? [];
  const project = projects.find((item) => item.id === projectId);
  const session = sessions.find((item) => item.id === sessionId);

  useEffect(() => {
    if (
      projectsQuery.isSuccess &&
      !projects.some((item) => item.id === projectId)
    )
      setProjectId(projects[0]?.id ?? "");
  }, [projects, projectId, projectsQuery.isSuccess]);
  useEffect(() => {
    if (
      sessionsQuery.isSuccess &&
      !sessions.some((item) => item.id === sessionId)
    )
      setSessionId(sessions.find((item) => !item.ended_at)?.id ?? "");
  }, [sessions, sessionId, sessionsQuery.isSuccess]);
  useEffect(() => {
    persist("memglide.project", projectId);
  }, [projectId]);
  useEffect(() => {
    persist("memglide.session", sessionId);
  }, [sessionId]);
  useEffect(() => {
    updateRetrieval(null);
    const previous = previousSession.current;
    client.removeQueries({
      predicate: (query) =>
        (query.queryKey[0] === "memories" &&
          ((query.queryKey[1] === previous && previous !== sessionId) ||
            (query.queryKey[1] === sessionId && Boolean(session?.ended_at)))) ||
        (query.queryKey[0] === "passport" &&
          ((query.queryKey[2] === previous && previous !== sessionId) ||
            (query.queryKey[2] === sessionId && Boolean(session?.ended_at)))),
    });
    previousSession.current = sessionId;
    try {
      sessionStorage.removeItem("memglide.retrieval");
    } catch {
      /* Remove data persisted by earlier dashboard versions when storage is available. */
    }
  }, [sessionId, projectId, session?.ended_at, client]);
  useEffect(() => {
    const media = window.matchMedia("(prefers-color-scheme: light)");
    function applyTheme() {
      document.documentElement.dataset.theme =
        settings.data?.theme === "system"
          ? media.matches
            ? "light"
            : "dark"
          : (settings.data?.theme ?? "dark");
    }
    applyTheme();
    media.addEventListener("change", applyTheme);
    return () => media.removeEventListener("change", applyTheme);
  }, [settings.data?.theme]);

  function selectProject(id: string) {
    if (id !== projectId) {
      updateRetrieval(null);
      setProjectId(id);
      setSessionId("");
    }
  }
  function selectSession(id: string) {
    if (id !== sessionId) {
      updateRetrieval(null);
      setSessionId(id);
    }
  }
  function setRetrieval(value: Retrieval | null) {
    if (value && value.session_id !== activeSession.current) return;
    updateRetrieval(value);
  }
  async function refresh() {
    await client.invalidateQueries();
  }

  return (
    <WorkspaceContext.Provider
      value={{
        projectId,
        sessionId,
        project,
        session,
        projects,
        sessions,
        projectsLoading: projectsQuery.isLoading,
        sessionsLoading: sessionsQuery.isLoading,
        projectsError: projectsQuery.error,
        sessionsError: sessionsQuery.error,
        selectProject,
        selectSession,
        refresh,
        retrieval,
        setRetrieval,
      }}
    >
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace() {
  const value = useContext(WorkspaceContext);
  if (!value) throw new Error("WorkspaceProvider is required");
  return value;
}
