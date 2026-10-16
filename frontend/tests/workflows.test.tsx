import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "../src/App";
import type {
  Memory,
  Overview,
  Passport,
  Project,
  Retrieval,
  Session,
  Settings,
} from "../src/types";

const now = Date.now() / 1000;
const project: Project = {
  id: "p1",
  name: "auth-service",
  path: "/approved/auth-service",
  branch: "main",
  git_state: { dirty: false },
  created_at: now,
  indexed_at: now,
  index_stats: {
    file_count: 3,
    symbol_count: 5,
    languages: { python: 3 },
    ignored_files: [{ path: ".env", reason: "credential file" }],
    errors: [],
  },
};
const session: Session = {
  id: "s1",
  project_id: "p1",
  task: "Review authentication",
  created_at: now,
  last_activity: now,
  expires_at: now + 3600,
  absolute_expires_at: now + 28800,
  ended_at: null,
};
const defaults: Settings = {
  session_ttl_minutes: 60,
  max_session_hours: 8,
  context_token_budget: 4000,
  ignored_directories: [],
  max_file_size: 512000,
  watch_enabled: true,
  event_logging: true,
  theme: "dark",
};
const memory: Memory = {
  id: "m1",
  session_id: "s1",
  category: "verified_fix",
  content: "JWT verification rejects expired tokens.",
  provenance: "Verified tests/test_auth.py",
  created_at: now,
  updated_at: now,
  stale: false,
  freshness: "Current",
  sources: [{ path: "auth.py", hash: "a".repeat(64) }],
};
const passport: Passport = {
  retrieval_id: "r1",
  session_id: "s1",
  status: "Partial",
  source_freshness: "Current",
  evidence_quality: "Static source evidence; inspect unresolved imports.",
  selected_files: [{ path: "auth.py", hash: "a".repeat(64) }],
  selected_symbols: [
    { path: "auth.py", symbol: "verify_token", start_line: 1 },
  ],
  verified_source_hashes: { "auth.py": "a".repeat(64) },
  dependencies: [],
  unresolved_dependencies: [
    { source_file: "auth.py", reference: "jwt.decode", resolved: false },
  ],
  related_tests: ["tests/test_auth.py"],
  missing_context: ["External JWT implementation requires inspection."],
  recommended_next_retrievals: ["Inspect tests/test_auth.py"],
  token_budget: 4000,
  estimated_tokens_returned: 800,
};
const retrieval: Retrieval = {
  retrieval_id: "r1",
  session_id: "s1",
  project_id: "p1",
  query: "verify_token",
  level: 1,
  budget: 4000,
  estimated_tokens: 800,
  token_estimate_method: "Characters / 4 across complete response",
  items: [
    {
      path: "auth.py",
      symbol: "verify_token",
      signature: "def verify_token(token)",
      start_line: 1,
      end_line: 3,
      hash: "a".repeat(64),
      snippet: "def verify_token(token):\n    return jwt.decode(token)",
      reason: "Exact symbol match",
      freshness: "Current",
    },
  ],
  memories: [],
  dependencies: [],
  warnings: ["External JWT implementation requires inspection."],
  truncated: false,
  passport,
};

interface State {
  projects: Project[];
  sessions: Session[];
  memories: Memory[];
  settings: Settings;
  requests: { path: string; method: string; body: Record<string, unknown> }[];
}
let state: State;

function response(value: unknown, status = 200) {
  return new Response(JSON.stringify(value), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

beforeEach(() => {
  state = {
    projects: [project],
    sessions: [session],
    memories: [memory],
    settings: { ...defaults },
    requests: [],
  };
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: string, options: RequestInit = {}) => {
      const url = new URL(input, "http://localhost");
      const path = url.pathname.replace(/^\/api/, "");
      const method = options.method ?? "GET";
      const body = options.body
        ? (JSON.parse(String(options.body)) as Record<string, unknown>)
        : {};
      state.requests.push({ path: url.pathname + url.search, method, body });
      if (path === "/health")
        return response({ status: "ok", local_only: true, version: "0.1.0" });
      if (path === "/projects" && method === "POST") {
        const added = {
          ...project,
          id: "p2",
          name: "new-app",
          path: String(body.path),
        };
        state.projects.push(added);
        return response(added, 201);
      }
      if (path === "/projects") return response(state.projects);
      if (path === "/sessions" && method === "POST") {
        const added = {
          ...session,
          id: "s2",
          project_id: String(body.project_id),
          task: String(body.task),
        };
        state.sessions.push(added);
        return response(added, 201);
      }
      if (path === "/sessions")
        return response(
          state.sessions.filter(
            (item) =>
              !url.searchParams.get("project_id") ||
              item.project_id === url.searchParams.get("project_id"),
          ),
        );
      if (path === "/settings" && method === "PUT") {
        state.settings = { ...state.settings, ...body };
        return response(state.settings);
      }
      if (path === "/sessions/s1" && method === "DELETE") {
        const ended = { ...session, ended_at: now };
        state.sessions = [ended];
        return response(ended);
      }
      if (path === "/settings") return response(state.settings);
      if (path === "/overview") {
        const overview: Overview = {
          status: "ok",
          service: "Memglide",
          version: "0.1.0",
          mcp: {
            status: "not_observable",
            detail:
              "STDIO clients connect independently; no client connection inferred",
          },
          counts: {
            projects: state.projects.length,
            sessions: state.sessions.length,
            files: 3,
            symbols: 5,
            memories: state.memories.length,
            retrievals: 0,
            database_bytes: 2048,
          },
          projects: state.projects,
          sessions: state.sessions,
          recent_retrievals: [],
          recent_events: [],
          warnings: [],
          settings: state.settings,
        };
        return response(overview);
      }
      if (/\/sessions\/[^/]+\/memories$/.test(path) && method === "GET")
        return response(
          state.memories.filter(
            (item) =>
              (!url.searchParams.get("query") ||
                item.content
                  .toLowerCase()
                  .includes(url.searchParams.get("query")!.toLowerCase())) &&
              (!url.searchParams.get("category") ||
                item.category === url.searchParams.get("category")),
          ),
        );
      if (/\/sessions\/[^/]+\/memories$/.test(path) && method === "POST") {
        const added = { ...memory, ...body, id: "m2", sources: [] } as Memory;
        state.memories.push(added);
        return response(added, 201);
      }
      if (/\/sessions\/[^/]+\/clear$/.test(path)) {
        state.sessions = [];
        state.memories = [];
        return response({ cleared: true });
      }
      if (path === "/context")
        return response({
          ...retrieval,
          query: body.query,
          level: body.level,
          budget: body.budget,
        });
      if (path === "/context/r1/expand")
        return response({
          ...retrieval,
          level: body.level,
          budget: body.budget,
        });
      if (path === "/context/r1/passport") return response(passport);
      if (path === "/events")
        return response([
          {
            id: "e1",
            project_id: "p1",
            session_id: "s1",
            type: "memory_saved",
            detail: { memory_id: "m1" },
            created_at: now,
          },
          {
            id: "e2",
            project_id: "p1",
            session_id: "s1",
            type: "context_retrieved",
            detail: { query: "verify_token" },
            created_at: now,
          },
        ]);
      return response(
        { error: { message: `Unhandled test route: ${method} ${path}` } },
        404,
      );
    }),
  );
});

function mount(path = "/") {
  const client = new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
      mutations: { retry: false },
    },
  });
  return {
    ...render(
      <QueryClientProvider client={client}>
        <MemoryRouter initialEntries={[path]}>
          <App />
        </MemoryRouter>
      </QueryClientProvider>,
    ),
    client,
  };
}

describe("dashboard workflows", () => {
  it("waits for delayed sessions before confirming passport URL alignment", async () => {
    state.sessions.unshift({ ...session, id: "s2", task: "Newest task" });
    const originalFetch = globalThis.fetch;
    let release!: () => void;
    const pending = new Promise<void>((resolve) => {
      release = resolve;
    });
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: string, options?: RequestInit) => {
        if (input.startsWith("/api/sessions?")) await pending;
        return originalFetch(input, options);
      }),
    );
    mount("/passport?retrieval=r1&session=s1");
    expect(
      await screen.findByRole("heading", { name: "Partial evidence" }),
    ).toBeInTheDocument();
    release();
    await waitFor(() =>
      expect(screen.getByRole("combobox", { name: "SESSION" })).toHaveValue(
        "s1",
      ),
    );
    await userEvent.selectOptions(
      screen.getByRole("combobox", { name: "SESSION" }),
      "s2",
    );
    expect(screen.getByRole("combobox", { name: "SESSION" })).toHaveValue("s2");
  });

  it("opens a passport URL for its own session without losing the pending query during auto-selection", async () => {
    state.sessions.push({ ...session, id: "s2", task: "Second task" });
    localStorage.setItem("memglide.session", "s1");
    mount("/passport?retrieval=r1&session=s2");
    expect(
      await screen.findByRole("heading", { name: "Partial evidence" }),
    ).toBeInTheDocument();
    await waitFor(() =>
      expect(screen.getByRole("combobox", { name: "SESSION" })).toHaveValue(
        "s2",
      ),
    );
    expect(
      state.requests.some(
        (request) => request.path === "/api/context/r1/passport?session_id=s2",
      ),
    ).toBe(true);
  });

  it("keeps ended sessions available for deletion without recalling their memories", async () => {
    const { client } = mount("/memory");
    expect(await screen.findByText(memory.content)).toBeInTheDocument();
    const recalls = state.requests.filter((request) =>
      request.path.includes("/memories"),
    ).length;
    await userEvent.click(
      screen.getByRole("button", { name: "End selected session" }),
    );
    await userEvent.click(
      within(screen.getByRole("dialog")).getByRole("button", {
        name: "End session",
      }),
    );
    expect(
      await screen.findByRole("heading", { name: "This session has ended" }),
    ).toBeInTheDocument();
    expect(screen.queryByText(memory.content)).not.toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Save a memory" }),
    ).toBeDisabled();
    expect(screen.getByRole("combobox", { name: "SESSION" })).toHaveValue("s1");
    expect(
      screen.getByRole("button", {
        name: "Delete selected session and memory",
      }),
    ).toBeEnabled();
    expect(
      state.requests.filter((request) => request.path.includes("/memories")),
    ).toHaveLength(recalls);
    expect(client.getQueriesData({ queryKey: ["memories"] })).toHaveLength(0);
  });

  it("renders ignored file paths and exclusion reasons from the index", async () => {
    mount("/projects");
    await userEvent.click(
      await screen.findByRole("button", { name: "Index details" }),
    );
    expect(screen.getByText(".env")).toBeInTheDocument();
    expect(screen.getByText("credential file")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Index errors" }),
    ).toBeInTheDocument();
  });

  it("shows real empty states and registers a repository through the API", async () => {
    state.projects = [];
    state.sessions = [];
    mount("/projects");
    expect(
      await screen.findByRole("heading", {
        name: "Your first project starts here",
      }),
    ).toBeInTheDocument();
    await userEvent.click(
      screen.getAllByRole("button", { name: "Add repository" })[0],
    );
    await userEvent.type(
      screen.getByLabelText("Absolute repository path"),
      "/approved/new-app",
    );
    await userEvent.click(
      screen.getByRole("button", { name: "Register & index" }),
    );
    expect(
      await screen.findByRole("heading", { name: "new-app" }),
    ).toBeInTheDocument();
    expect(state.requests).toContainEqual({
      path: "/api/projects",
      method: "POST",
      body: { path: "/approved/new-app" },
    });
    expect(screen.getByRole("combobox", { name: "PROJECT" })).toHaveValue("p2");
  });

  it("starts and selects sessions and clears their cached task data on deletion", async () => {
    mount("/memory");
    expect(await screen.findByText(memory.content)).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "New session" }));
    await userEvent.type(
      screen.getByLabelText("Task"),
      "Verify logout behavior",
    );
    await userEvent.click(
      screen.getByRole("button", { name: "Start session" }),
    );
    await waitFor(() =>
      expect(screen.getByRole("combobox", { name: "SESSION" })).toHaveValue(
        "s2",
      ),
    );
    await userEvent.click(
      screen.getByRole("button", {
        name: "Delete selected session and memory",
      }),
    );
    await userEvent.click(
      within(screen.getByRole("dialog")).getByRole("button", {
        name: "Delete session",
      }),
    );
    await waitFor(() =>
      expect(screen.getByRole("combobox", { name: "SESSION" })).toHaveValue(""),
    );
    expect(screen.queryByText(memory.content)).not.toBeInTheDocument();
    expect(
      await screen.findByRole("heading", {
        name: "A session gives memory a home",
      }),
    ).toBeInTheDocument();
  });

  it("searches and filters memories and saves explicit provenance", async () => {
    mount("/memory");
    expect(await screen.findByText(memory.content)).toBeInTheDocument();
    await userEvent.type(
      screen.getByRole("textbox", { name: "Search memories" }),
      "missing-symbol",
    );
    expect(
      await screen.findByRole("heading", { name: "No matching memories" }),
    ).toBeInTheDocument();
    expect(
      state.requests.some((request) =>
        request.path.includes("query=missing-symbol"),
      ),
    ).toBe(true);
    await userEvent.click(
      screen.getByRole("button", { name: "Clear filters" }),
    );
    expect(await screen.findByText(memory.content)).toBeInTheDocument();
    await userEvent.click(
      screen.getAllByRole("button", { name: "Save a memory" })[0],
    );
    await userEvent.type(
      screen.getByLabelText("Finding"),
      "Review the logout redirect before shipping.",
    );
    await userEvent.click(screen.getByRole("button", { name: "Save memory" }));
    expect(
      await screen.findByText("Review the logout redirect before shipping."),
    ).toBeInTheDocument();
    expect(
      state.requests.find(
        (request) =>
          request.method === "POST" && request.path.endsWith("/memories"),
      )?.body.provenance,
    ).toBe("User submitted through the local dashboard");
    await userEvent.click(screen.getByRole("button", { name: "Verified Fix" }));
    await waitFor(() =>
      expect(
        screen.queryByText("Review the logout redirect before shipping."),
      ).not.toBeInTheDocument(),
    );
  });

  it("retrieves ranked evidence, expands depth, and renders source hashes and passport warnings", async () => {
    mount("/context");
    const submit = await screen.findByRole("button", {
      name: "Retrieve context",
    });
    expect(submit).toBeDisabled();
    await userEvent.type(
      screen.getByLabelText("WHAT DO YOU NEED TO UNDERSTAND?"),
      "verify_token",
    );
    await waitFor(() => expect(submit).toBeEnabled());
    await userEvent.click(submit);
    expect(await screen.findByText("Exact symbol match")).toBeInTheDocument();
    expect(
      screen.getByLabelText("Source snippet for auth.py"),
    ).toHaveTextContent("jwt.decode(token)");
    expect(sessionStorage.getItem("memglide.retrieval")).toBeNull();
    await userEvent.click(
      screen.getByRole("button", { name: "Expand to level 2" }),
    );
    expect(
      await screen.findByRole("button", { name: "Expand to level 3" }),
    ).toBeInTheDocument();
    expect(
      state.requests.find(
        (request) => request.path === "/api/context/r1/expand",
      )?.body,
    ).toMatchObject({ session_id: "s1", level: 2, budget: 4000 });
    await userEvent.click(screen.getByRole("link", { name: "View passport" }));
    expect(
      await screen.findByRole("heading", { name: "Partial evidence" }),
    ).toBeInTheDocument();
    expect(
      screen.getByText("External JWT implementation requires inspection."),
    ).toBeInTheDocument();
    expect(screen.getByText("tests/test_auth.py")).toBeInTheDocument();
    expect(screen.getByText("Unresolved")).toBeInTheDocument();
    expect(screen.getByTitle("a".repeat(64))).toBeInTheDocument();
  });

  it("persists settings and applies the saved theme from the backend", async () => {
    mount("/settings");
    const budget = await screen.findByRole("spinbutton", {
      name: "Default context token budget",
    });
    await userEvent.clear(budget);
    await userEvent.type(budget, "6000");
    await userEvent.click(screen.getByRole("button", { name: "Light" }));
    await userEvent.type(
      screen.getByLabelText("Ignored directories"),
      "coverage\ngenerated",
    );
    await userEvent.click(
      screen.getByRole("switch", { name: "Record local events" }),
    );
    await userEvent.click(
      screen.getByRole("button", { name: "Save settings" }),
    );
    expect(await screen.findByRole("status")).toHaveTextContent(
      "Settings saved",
    );
    expect(state.settings).toMatchObject({
      context_token_budget: 6000,
      theme: "light",
      ignored_directories: ["coverage", "generated"],
      event_logging: false,
    });
    await waitFor(() =>
      expect(document.documentElement).toHaveAttribute("data-theme", "light"),
    );
    expect(
      screen.getByRole("button", { name: "Save settings" }),
    ).toBeDisabled();
  });

  it("filters actual timeline events and exposes event detail", async () => {
    mount("/timeline");
    expect(await screen.findByText("verify_token")).toBeInTheDocument();
    await userEvent.selectOptions(
      screen.getByLabelText("Event type"),
      "memory_saved",
    );
    expect(screen.queryByText("verify_token")).not.toBeInTheDocument();
    await userEvent.click(
      screen.getByRole("button", { name: "Event details" }),
    );
    expect(screen.getByText(/"memory_id": "m1"/)).toBeInTheDocument();
  });

  it("reports service errors without displaying invented overview metrics", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: string) =>
        input === "/api/overview"
          ? response(
              { error: { message: "Local database is unavailable" } },
              503,
            )
          : response(
              input === "/api/settings"
                ? defaults
                : input === "/api/health"
                  ? { status: "ok" }
                  : [],
            ),
      ),
    );
    mount("/");
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Local database is unavailable",
    );
    expect(screen.queryByText("Indexed files")).not.toBeInTheDocument();
  });
});
