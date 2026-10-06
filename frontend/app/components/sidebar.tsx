"use client";

import { useEffect, useState } from "react";
import { useChatStore } from "../store/chat_store";

export default function Sidebar() {
  const {
    sessions,
    activeSessionId,
    setActiveSession,
    createNewSession,
    deleteSession,
    renameSession,
  } = useChatStore();

  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <aside className="flex w-72 flex-col border-r bg-gray-50">
      <div className="border-b p-4">
        <button
          onClick={createNewSession}
          className="flex w-full items-center justify-center gap-2 rounded-xl border bg-white px-4 py-2 text-sm font-medium transition hover:bg-gray-100"
        >
          <span>＋</span>
          <span>New chat</span>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-2">
        <div className="space-y-2">
          {sessions.map((session) => {
            const isActive = activeSessionId === session.id;

            return (
              <div
                key={session.id}
                className={`group rounded-xl border transition-all duration-200 ${
                  isActive
                    ? "border-gray-300 bg-white shadow-sm"
                    : "border-transparent bg-transparent hover:border-gray-200 hover:bg-white hover:shadow-sm"
                }`}
              >
                <div className="flex items-start gap-2 p-3">
                  <button
                    onClick={() => setActiveSession(session.id)}
                    className="flex min-w-0 flex-1 items-start gap-2 text-left"
                  >
                    <span className="pt-0.5 text-sm">💬</span>

                    <div className="min-w-0 flex-1">
                      <div className="truncate text-sm font-medium">
                        {session.title}
                      </div>

                      {session.knowledgeBaseLabel &&
                        session.knowledgeBaseLabel !== "Default Science Pack" && (
                          <div className="mt-0.5 flex items-center gap-1 truncate text-xs text-blue-600">
                            <span>📄</span>
                            <span className="truncate">
                              {session.knowledgeBaseLabel}
                            </span>
                          </div>
                        )}

                      <div className="mt-1 text-xs text-gray-500">
                        {mounted
                          ? new Date(session.updatedAt).toLocaleString()
                          : ""}
                      </div>
                    </div>
                  </button>

                  <div className="flex items-center gap-1 opacity-0 transition group-hover:opacity-100">
                    <button
                      type="button"
                      onClick={() => {
                        const nextTitle = window.prompt(
                          "Rename chat",
                          session.title,
                        );

                        if (nextTitle) {
                          renameSession(session.id, nextTitle);
                        }
                      }}
                      className="rounded-md p-1 text-sm hover:bg-gray-100"
                      aria-label={`Rename ${session.title}`}
                      title="Rename chat"
                    >
                      ✏️
                    </button>

                    <button
                      type="button"
                      onClick={() => {
                        const confirmed = window.confirm(
                          `Delete chat "${session.title}"?`,
                        );

                        if (confirmed) {
                          deleteSession(session.id);
                        }
                      }}
                      className="rounded-md p-1 text-sm hover:bg-gray-100"
                      aria-label={`Delete ${session.title}`}
                      title="Delete chat"
                    >
                      🗑
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </aside>
  );
}
