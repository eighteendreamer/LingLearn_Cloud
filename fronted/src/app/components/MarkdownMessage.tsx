import type { ReactNode } from "react";
import { Link } from "react-router";

interface MarkdownMessageProps {
  content: string;
  className?: string;
}

function renderInline(text: string): ReactNode[] {
  const tokens = text.split(/(\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*)/g).filter(Boolean);
  return tokens.map((part, index) => {
    const linkMatch = part.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
    if (linkMatch) {
      const [, label, href] = linkMatch;
      const isInternal = href.startsWith("/");
      if (isInternal) {
        return (
          <Link key={index} to={href} className="font-medium text-emerald-600 underline underline-offset-2">
            {label}
          </Link>
        );
      }
      return (
        <a
          key={index}
          href={href}
          target="_blank"
          rel="noreferrer"
          className="font-medium text-emerald-600 underline underline-offset-2"
        >
          {label}
        </a>
      );
    }

    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }
    return <span key={index}>{part}</span>;
  });
}

export function MarkdownMessage({ content, className = "" }: MarkdownMessageProps) {
  const blocks: ReactNode[] = [];
  const lines = content.split(/\r?\n/);
  let listItems: string[] = [];
  let codeLines: string[] = [];
  let inCodeBlock = false;

  const flushList = () => {
    if (listItems.length === 0) {
      return;
    }
    blocks.push(
      <ul key={`list-${blocks.length}`} className="my-2 list-disc space-y-1 pl-5">
        {listItems.map((item, index) => (
          <li key={index}>{renderInline(item)}</li>
        ))}
      </ul>
    );
    listItems = [];
  };

  const flushCode = () => {
    if (codeLines.length === 0) {
      return;
    }
    blocks.push(
      <pre key={`code-${blocks.length}`} className="my-2 overflow-x-auto rounded-lg bg-gray-900 px-3 py-2 text-xs text-gray-100">
        <code>{codeLines.join("\n")}</code>
      </pre>
    );
    codeLines = [];
  };

  lines.forEach((line) => {
    const trimmed = line.trim();

    if (trimmed.startsWith("```")) {
      if (inCodeBlock) {
        flushCode();
      } else {
        flushList();
      }
      inCodeBlock = !inCodeBlock;
      return;
    }

    if (inCodeBlock) {
      codeLines.push(line);
      return;
    }

    if (!trimmed) {
      flushList();
      return;
    }

    const heading = trimmed.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      flushList();
      const Tag = heading[1].length === 1 ? "h3" : heading[1].length === 2 ? "h4" : "h5";
      blocks.push(
        <Tag key={`heading-${blocks.length}`} className="mb-1 mt-2 font-semibold">
          {renderInline(heading[2])}
        </Tag>
      );
      return;
    }

    const listMatch = trimmed.match(/^([-*•]|\d+\.)\s+(.+)$/);
    if (listMatch) {
      listItems.push(listMatch[2]);
      return;
    }

    flushList();
    blocks.push(
      <p key={`p-${blocks.length}`} className="my-1">
        {renderInline(trimmed)}
      </p>
    );
  });

  flushList();
  flushCode();

  return <div className={`whitespace-normal break-words ${className}`}>{blocks}</div>;
}
