"use client";

import { useEffect } from "react";
import Sidebar from "./components/sidebar";
import ChatView from "./components/chat-view";
import { useChatStore } from "./store/chat_store";

export default function HomePage() {
  const { sessions, activeSessionId, createNewSession, hasHydrated } =
    useChatStore();

  useEffect(() => {
    if (hasHydrated && sessions.length === 0 && !activeSessionId) {
      createNewSession();
    }
  }, [hasHydrated, sessions.length, activeSessionId, createNewSession]);

  if (!hasHydrated) {
    return (
      <main className="h-screen flex items-center justify-center">
        Loading...
      </main>
    );
  }

  return (
    <main className="h-screen">
      <div className="flex h-full">
        <Sidebar />
        <ChatView />
      </div>
    </main>
  );
}
