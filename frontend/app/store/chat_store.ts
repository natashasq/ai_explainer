import { create } from "zustand";
import { persist } from "zustand/middleware";
import { explainFromMessages, streamAnswerFromMessages } from "../lib/api";
import { ChatMessage, ChatSession } from "../types/chat";

type ChatStore = {
  sessions: ChatSession[];
  activeSessionId: string | null;
  loading: boolean;
  error: string;
  hasHydrated: boolean;

  setHasHydrated: (value: boolean) => void;
  createNewSession: () => void;
  setActiveSession: (sessionId: string) => void;
  deleteSession: (sessionId: string) => void;
  renameSession: (sessionId: string, title: string) => void;
  getActiveSession: () => ChatSession | null;
  sendQuestion: (question: string) => Promise<void>;
  attachKnowledgeBaseToActiveSession: (
    knowledgeBaseId: string,
    label: string,
  ) => void;
};

function createId() {
  return crypto.randomUUID();
}

function createEmptySession(): ChatSession {
  const now = new Date().toISOString();

  return {
    id: createId(),
    title: "New chat",
    messages: [],
    createdAt: now,
    updatedAt: now,
    knowledgeBaseId: "default",
    knowledgeBaseLabel: "Default Science Pack",
  };
}

function generateSessionTitle(question: string) {
  const trimmed = question.trim();
  if (!trimmed) return "New chat";
  return trimmed.length > 40 ? `${trimmed.slice(0, 40)}...` : trimmed;
}

function moveSessionToTop(
  sessions: ChatSession[],
  sessionId: string,
  updater: (session: ChatSession) => ChatSession,
): ChatSession[] {
  const target = sessions.find((session) => session.id === sessionId);
  if (!target) return sessions;

  const updatedTarget = updater(target);
  const remaining = sessions.filter((session) => session.id !== sessionId);

  return [updatedTarget, ...remaining];
}

export const useChatStore = create<ChatStore>()(
  persist(
    (set, get) => ({
      sessions: [],
      activeSessionId: null,
      loading: false,
      error: "",
      hasHydrated: false,

      setHasHydrated: (value) => set({ hasHydrated: value }),

      createNewSession: () => {
        const session = createEmptySession();

        set((state) => ({
          sessions: [session, ...state.sessions],
          activeSessionId: session.id,
          error: "",
        }));
      },

      setActiveSession: (sessionId: string) => {
        set({ activeSessionId: sessionId, error: "" });
      },

      deleteSession: (sessionId: string) => {
        set((state) => {
          const remainingSessions = state.sessions.filter(
            (session) => session.id !== sessionId,
          );

          const isDeletingActiveSession = state.activeSessionId === sessionId;

          let nextActiveSessionId = state.activeSessionId;
          if (isDeletingActiveSession) {
            nextActiveSessionId =
              remainingSessions.length > 0 ? remainingSessions[0].id : null;
          }

          return {
            sessions: remainingSessions,
            activeSessionId: nextActiveSessionId,
            error: "",
          };
        });
      },

      renameSession: (sessionId: string, title: string) => {
        const trimmed = title.trim();
        if (!trimmed) return;

        set((state) => ({
          sessions: state.sessions.map((session) =>
            session.id === sessionId
              ? {
                  ...session,
                  title: trimmed,
                  updatedAt: new Date().toISOString(),
                }
              : session,
          ),
        }));
      },

      getActiveSession: () => {
        const { sessions, activeSessionId } = get();
        if (!activeSessionId) return null;
        return (
          sessions.find((session) => session.id === activeSessionId) ?? null
        );
      },

      sendQuestion: async (question: string) => {
        const trimmed = question.trim();
        if (!trimmed || get().loading) return;

        let { activeSessionId, sessions } = get();

        if (!activeSessionId) {
          const newSession = createEmptySession();
          sessions = [newSession, ...sessions];
          activeSessionId = newSession.id;

          set({
            sessions,
            activeSessionId,
          });
        }

        const activeSession = sessions.find(
          (session) => session.id === activeSessionId,
        );

        if (!activeSession) return;

        const userMessage: ChatMessage = {
          id: createId(),
          role: "user",
          content: trimmed,
        };
        const knowledgeBaseId = activeSession.knowledgeBaseId;
        const assistantMessageId = createId();

        const assistantPlaceholder: ChatMessage = {
          id: assistantMessageId,
          role: "assistant",
          content: "",
          suggestedQuestions: [],
          sources: [],
        };

        const updatedMessages = [
          ...activeSession.messages,
          userMessage,
          assistantPlaceholder,
        ];

        const now = new Date().toISOString();

        set((state) => ({
          sessions: moveSessionToTop(
            state.sessions,
            activeSessionId!,
            (session) => ({
              ...session,
              messages: updatedMessages,
              updatedAt: now,
              title:
                session.messages.length === 0
                  ? generateSessionTitle(trimmed)
                  : session.title,
            }),
          ),
          loading: true,
          error: "",
        }));

        try {
          const historyForApi = [...activeSession.messages, userMessage]
            .slice(-6)
            .map((message) => ({
              role: message.role,
              content: message.content,
            }));

          await streamAnswerFromMessages(
            historyForApi,
            knowledgeBaseId,
            (chunk) => {
              set((state) => ({
                sessions: moveSessionToTop(
                  state.sessions,
                  activeSessionId!,
                  (session) => ({
                    ...session,
                    messages: session.messages.map((message) =>
                      message.id === assistantMessageId &&
                      message.role === "assistant"
                        ? {
                            ...message,
                            content: message.content + chunk,
                          }
                        : message,
                    ),
                    updatedAt: new Date().toISOString(),
                  }),
                ),
              }));
            },
          );

          const suggestionsData = await explainFromMessages(
            historyForApi,
            knowledgeBaseId,
          );

          set((state) => ({
            sessions: moveSessionToTop(
              state.sessions,
              activeSessionId!,
              (session) => ({
                ...session,
                messages: session.messages.map((message) =>
                  message.id === assistantMessageId &&
                  message.role === "assistant"
                    ? {
                        ...message,
                        suggestedQuestions: suggestionsData.suggested_questions,
                        sources: suggestionsData.sources,
                      }
                    : message,
                ),
                updatedAt: new Date().toISOString(),
              }),
            ),
          }));
        } catch (err) {
          console.error(err);

          const isKnowledgeBaseNotFound =
            err instanceof Error && err.message.includes("404");

          set((state) => ({
            sessions: moveSessionToTop(
              state.sessions,
              activeSessionId!,
              (session) => ({
                ...session,
                messages: session.messages.filter(
                  (message) => message.id !== assistantMessageId,
                ),
                ...(isKnowledgeBaseNotFound
                  ? {
                      knowledgeBaseId: "default",
                      knowledgeBaseLabel: "Default Science Pack",
                    }
                  : {}),
              }),
            ),
            error: isKnowledgeBaseNotFound
              ? "The uploaded document is no longer available. Switched back to the default knowledge base."
              : "Something went wrong while generating the answer.",
          }));
        } finally {
          set({ loading: false });
        }
      },
      attachKnowledgeBaseToActiveSession: (
        knowledgeBaseId: string,
        label: string,
      ) => {
        const { activeSessionId } = get();
        if (!activeSessionId) return;

        set((state) => ({
          sessions: state.sessions.map((session) =>
            session.id === activeSessionId
              ? {
                  ...session,
                  knowledgeBaseId,
                  knowledgeBaseLabel: label,
                  updatedAt: new Date().toISOString(),
                }
              : session,
          ),
        }));
      },
    }),

    {
      name: "ai-chat-storage",
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      },
    },
  ),
);
