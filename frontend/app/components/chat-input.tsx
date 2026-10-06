"use client";

import { useEffect, useRef, useState } from "react";

type ChatInputProps = {
  loading: boolean;
  onSend: (value: string) => Promise<void> | void;
  autoFocusSignal?: string | number;
};

export default function ChatInput({
  loading,
  onSend,
  autoFocusSignal,
}: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    adjustHeight();
  }, [value]);

  useEffect(() => {
    textareaRef.current?.focus();
  }, [autoFocusSignal]);

  function adjustHeight() {
    const textarea = textareaRef.current;
    if (!textarea) return;

    textarea.style.height = "0px";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 220)}px`;
  }

  async function handleSubmit() {
    const trimmed = value.trim();
    if (!trimmed || loading) return;

    await onSend(trimmed);
    setValue("");

    requestAnimationFrame(() => {
      const textarea = textareaRef.current;
      if (!textarea) return;
      textarea.style.height = "0px";
      textarea.focus();
    });
  }

  async function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      await handleSubmit();
    }
  }

  return (
    <div className="border-t px-6 py-4">
      <div className="rounded-2xl border bg-white p-3 shadow-sm">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask something..."
          rows={1}
          className="max-h-55 min-h-6 w-full resize-none overflow-y-auto bg-transparent outline-none"
        />

        <div className="mt-3 flex items-center justify-between">
          <p className="text-xs text-gray-500">
            Enter to send · Shift+Enter for new line
          </p>

          <button
            type="button"
            onClick={handleSubmit}
            disabled={loading || !value.trim()}
            className="rounded-xl border px-4 py-2 text-sm disabled:opacity-50"
          >
            {loading ? "Sending..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
