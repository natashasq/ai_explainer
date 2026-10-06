"use client";

import { useEffect, useRef } from "react";
import { useChatStore } from "../store/chat_store";
import ChatInput from "./chat-input";
import SourcePreview from "./source-preview";
import KnowledgeBaseUploader from "../components/knowledgebase_uloader";

export default function ChatView() {
  const { getActiveSession, loading, error, sendQuestion } = useChatStore();
  const activeSession = getActiveSession();

  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeSession?.messages, loading]);

  return (
    <div className="flex flex-1 flex-col">
      <header className="border-b px-6 py-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold">
              {activeSession?.title || "Explain the World"}
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Knowledge base:{" "}
              {activeSession?.knowledgeBaseLabel || "Default Science Pack"}
            </p>
          </div>

          <KnowledgeBaseUploader />
        </div>
      </header>

      <section className="flex-1 overflow-y-auto px-6 py-6">
        {!activeSession || activeSession.messages.length === 0 ? (
          <div className="flex h-full items-center justify-center">
            <div className="max-w-lg text-center">
              <h2 className="mb-3 text-2xl font-semibold">
                Start a new conversation
              </h2>
              <p className="text-gray-600">
                Try: Why is the sky blue? What is a black hole? How do vaccines
                work?
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {activeSession.messages.map((message) => {
              if (message.role === "user") {
                return (
                  <div key={message.id} className="flex justify-end">
                    <div className="max-w-[80%] rounded-2xl border px-4 py-3">
                      {message.content}
                    </div>
                  </div>
                );
              }

              return (
                <div key={message.id} className="flex justify-start">
                  <div className="max-w-[80%] rounded-2xl border px-4 py-3">
                    <div className="whitespace-pre-line leading-7">
                      {message.content}
                      {loading &&
                      activeSession?.messages[activeSession.messages.length - 1]
                        ?.id === message.id ? (
                        <span className="ml-1 inline-block animate-pulse">
                          ▍
                        </span>
                      ) : null}
                    </div>
                    {message.role === "assistant" &&
                      message?.sources?.length > 0 && (
                        <div className="mt-4">
                          <p className="mb-2 text-xs font-medium text-gray-500">
                            Sources used
                          </p>

                          <div className="space-y-2">
                            {message.sources.map((item, index) => (
                              <SourcePreview
                                key={`${item.source}-${index}`}
                                source={item.source}
                                text={item?.text}
                              />
                            ))}
                          </div>
                        </div>
                      )}

                    <div className="mt-4 flex flex-wrap gap-2">
                      {message.suggestedQuestions.map((item) => (
                        <button
                          key={item}
                          type="button"
                          onClick={() => sendQuestion(item)}
                          disabled={loading}
                          className="rounded-full border px-3 py-2 text-sm disabled:opacity-50"
                        >
                          {item}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              );
            })}

            {loading &&
              activeSession?.messages[activeSession.messages.length - 1]
                ?.role !== "assistant" && (
                <div className="flex justify-start">
                  <div className="rounded-2xl border px-4 py-3 text-gray-500">
                    Thinking...
                  </div>
                </div>
              )}

            <div ref={bottomRef} />
          </div>
        )}
      </section>

      <div>
        {error ? (
          <p className="px-6 pb-2 text-sm text-red-600">{error}</p>
        ) : null}

        <ChatInput
          loading={loading}
          onSend={sendQuestion}
          autoFocusSignal={activeSession?.id ?? "no-session"}
        />
      </div>
    </div>
  );
}
