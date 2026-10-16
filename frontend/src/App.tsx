import { lazy, Suspense } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  ArrowUpRight,
  BookOpen,
  Box,
  BrainCircuit,
  Check,
  ChevronRight,
  Compass,
  Fingerprint,
  FolderGit2,
  LayoutDashboard,
  Settings2,
  ShieldCheck,
} from "lucide-react";
import {
  NavLink,
  Navigate,
  Route,
  Routes,
  useLocation,
} from "react-router-dom";
import { api } from "./api";
import { WorkspaceProvider } from "./state";
import { Badge, Loading } from "./components/ui";
import Sessions from "./components/Sessions";

const OverviewScreen = lazy(() => import("./screens/Overview"));
const ProjectsScreen = lazy(() => import("./screens/Projects"));
const MemoryScreen = lazy(() => import("./screens/Memory"));
const ContextScreen = lazy(() => import("./screens/Context"));
const PassportScreen = lazy(() => import("./screens/Passport"));
const TimelineScreen = lazy(() => import("./screens/Timeline"));
const SettingsScreen = lazy(() => import("./screens/Settings"));

const navigation = [
  { to: "/", label: "Overview", icon: LayoutDashboard },
  { to: "/projects", label: "Projects", icon: FolderGit2 },
  { to: "/memory", label: "Memory explorer", icon: BrainCircuit },
  { to: "/context", label: "Context explorer", icon: Compass },
  { to: "/passport", label: "Context passport", icon: Fingerprint },
  { to: "/timeline", label: "Session timeline", icon: Activity },
  { to: "/settings", label: "Settings", icon: Settings2 },
];

function Shell() {
  const location = useLocation();
  const active = navigation.find((item) => item.to === location.pathname);
  const health = useQuery({
    queryKey: ["health"],
    queryFn: () => api<{ status: string; version?: string }>("/health"),
    refetchInterval: 15000,
    retry: false,
  });
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <aside className="sidebar">
        <NavLink to="/" className="brand" aria-label="Memglide overview">
          <span className="brand-mark">
            <svg
              width="22"
              height="22"
              viewBox="0 0 24 24"
              fill="none"
              aria-hidden="true"
            >
              <path
                d="M3 18V6h4l5 8 5-8h4v12h-4v-6l-5 7-5-7v6H3Z"
                fill="currentColor"
              />
            </svg>
          </span>
          <span>
            memglide<span className="brand-dot">.</span>
          </span>
          <span className="version">V1</span>
        </NavLink>
        <div className="sidebar-label">WORKSPACE</div>
        <nav aria-label="Main navigation">
          {navigation.map(({ to, label, icon: Icon }, index) => (
            <NavLink
              key={to}
              end={to === "/"}
              to={to}
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""} ${index === 6 ? "nav-settings" : ""}`
              }
            >
              <Icon size={18} strokeWidth={1.6} />
              <span>{label}</span>
              {to === "/passport" && <span className="nav-new">CORE</span>}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="local-note">
            <ShieldCheck size={17} />
            <div>
              <strong>Local by design</strong>
              <p>Your code stays on this machine.</p>
            </div>
          </div>
          <a
            className="docs-link"
            href="/docs"
            target="_blank"
            rel="noreferrer"
          >
            <BookOpen size={16} />
            API documentation
            <ArrowUpRight size={14} />
          </a>
          <div className="sidebar-footer">
            <span
              className={`status-dot ${health.isSuccess ? "" : health.isError ? "dot-error" : "dot-wait"}`}
            />
            {health.isSuccess
              ? "Local service connected"
              : health.isError
                ? "Local service unavailable"
                : "Connecting to service"}
            <span>{health.data?.version ? `v${health.data.version}` : ""}</span>
          </div>
        </div>
      </aside>
      <div className="app-main">
        <header className="topbar">
          <div className="breadcrumb">
            <Box size={15} />
            <span>Workspace</span>
            <ChevronRight size={13} />
            <strong>{active?.label ?? "Overview"}</strong>
          </div>
          <Badge tone={health.isSuccess ? "green" : "neutral"}>
            <span
              className={`status-dot ${health.isSuccess ? "" : "dot-wait"}`}
            />
            {health.isSuccess ? "Localhost" : "Connecting"}
          </Badge>
        </header>
        <Sessions />
        <main id="main" className="main-content" tabIndex={-1}>
          <Suspense fallback={<Loading label="Opening workspace…" />}>
            <Routes>
              <Route path="/" element={<OverviewScreen />} />
              <Route path="/projects" element={<ProjectsScreen />} />
              <Route path="/memory" element={<MemoryScreen />} />
              <Route path="/context" element={<ContextScreen />} />
              <Route path="/passport" element={<PassportScreen />} />
              <Route path="/timeline" element={<TimelineScreen />} />
              <Route path="/settings" element={<SettingsScreen />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Suspense>
        </main>
        <footer className="main-footer">
          <span>
            MEMGLIDE <span className="footer-dot">/</span> LOCAL CONTEXT
            INTELLIGENCE
          </span>
          <span>
            <Check size={12} />
            Remember. Select. Verify. Expand.
          </span>
        </footer>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <WorkspaceProvider>
      <Shell />
    </WorkspaceProvider>
  );
}
