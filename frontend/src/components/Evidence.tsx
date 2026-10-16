import { ArrowRight, FileCode2, GitFork } from "lucide-react";
import { describe } from "../format";
import type { ContextItem, Dependency } from "../types";
import { Badge } from "./ui";

export function EvidenceCard({
  item,
  rank,
}: {
  item: ContextItem;
  rank: number;
}) {
  const start = item.start_line ?? item.line_start;
  const end = item.end_line ?? item.line_end;
  const hash = item.hash ?? item.source_hash;
  const reasons =
    item.reasons ??
    (Array.isArray(item.reason)
      ? item.reason
      : item.reason
        ? [item.reason]
        : []);
  return (
    <article className="evidence-card">
      <div className="evidence-heading">
        <span className="evidence-rank">{String(rank).padStart(2, "0")}</span>
        <FileCode2 size={17} />
        <div className="grow">
          <strong>
            {item.symbol ?? item.name ?? item.qualified_name ?? item.path}
          </strong>
          <p>
            <code>
              {item.path}
              {start ? `:${start}${end && end !== start ? `–${end}` : ""}` : ""}
            </code>
          </p>
        </div>
        <Badge
          tone={item.freshness?.toLowerCase() === "stale" ? "amber" : "green"}
        >
          {item.freshness ?? "Source reference"}
        </Badge>
      </div>
      {item.signature && <code className="signature">{item.signature}</code>}
      {(item.snippet ?? item.content) && (
        <pre
          className="code-block"
          tabIndex={0}
          aria-label={`Source snippet for ${item.path}`}
        >
          <code>{item.snippet ?? item.content}</code>
        </pre>
      )}
      <div className="evidence-footer">
        <div>
          {reasons.map((reason, index) => (
            <span key={index} className="reason">
              <span className="reason-dot" />
              {reason}
            </span>
          ))}
        </div>
        {hash && (
          <code title={`Source SHA-256: ${hash}`}>
            sha256:{hash.slice(0, 12)}
          </code>
        )}
      </div>
    </article>
  );
}

export function DependencyList({ items }: { items: (Dependency | string)[] }) {
  return (
    <div className="dependency-list">
      {items.map((dependency, index) =>
        typeof dependency === "string" ? (
          <div className="dependency-row" key={index}>
            <GitFork size={14} />
            <code>{dependency}</code>
          </div>
        ) : (
          <div className="dependency-row" key={index}>
            <GitFork size={14} />
            <div className="grow">
              <code>
                {dependency.source_file ?? dependency.source_symbol ?? "Source"}
              </code>
              <ArrowRight size={12} />
              <code>
                {dependency.target_file ??
                  dependency.target_symbol ??
                  dependency.reference ??
                  "Unresolved"}
              </code>
              {dependency.reference && (
                <p>
                  {dependency.kind ?? "reference"}: {dependency.reference}
                </p>
              )}
            </div>
            <Badge tone={dependency.resolved ? "green" : "amber"}>
              {dependency.resolved ? "Resolved" : "Unresolved"}
            </Badge>
          </div>
        ),
      )}
    </div>
  );
}

export function EvidenceList({
  items,
  empty,
}: {
  items: unknown[];
  empty: string;
}) {
  return items.length ? (
    <ul className="evidence-list">
      {items.map((item, index) => (
        <li key={index}>
          <span className="reason-dot" />
          <code>{describe(item)}</code>
        </li>
      ))}
    </ul>
  ) : (
    <p className="section-empty">{empty}</p>
  );
}
