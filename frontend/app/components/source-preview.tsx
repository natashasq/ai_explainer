"use client";

import { useState } from "react";
import { SourcePreviewProps } from "../types/chat";

export default function SourcePreview({
  source,
  text,
  previewLength = 180,
}: SourcePreviewProps) {
  const [expanded, setExpanded] = useState(false);

  const isLong = text.length > previewLength;
  const previewText = isLong ? `${text.slice(0, previewLength)}...` : text;

  return (
    <div className="rounded-xl border bg-gray-50 p-3">
      <p className="text-xs font-medium text-gray-700">{source}</p>

      <p className="mt-1 whitespace-pre-line text-xs leading-6 text-gray-600">
        {expanded ? text : previewText}
      </p>

      {isLong && (
        <button
          type="button"
          onClick={() => setExpanded((prev) => !prev)}
          className="mt-2 text-xs font-medium text-gray-700 underline underline-offset-2"
        >
          {expanded ? "Show less" : "Show more"}
        </button>
      )}
    </div>
  );
}
