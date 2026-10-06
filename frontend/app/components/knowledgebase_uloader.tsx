"use client";

import { useState } from "react";
import { uploadFile } from "../lib/api";
import { useChatStore } from "../store/chat_store";

export default function KnowledgeBaseUploader() {
  const [loading, setLoading] = useState(false);
  const { attachKnowledgeBaseToActiveSession, getActiveSession } = useChatStore();

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setLoading(true);

      const currentKbId = getActiveSession()?.knowledgeBaseId;
      const result = await uploadFile(file, currentKbId);

      const currentLabel = getActiveSession()?.knowledgeBaseLabel;
      const isFirstUpload = !currentLabel || currentLabel === "Default Science Pack";
      const newLabel = isFirstUpload ? result.filename : `${currentLabel}, ${result.filename}`;

      attachKnowledgeBaseToActiveSession(result.knowledge_base_id, newLabel);
    } catch (error) {
      console.error(error);
      alert("Failed to upload file.");
    } finally {
      setLoading(false);
      e.target.value = "";
    }
  }

  return (
    <label className="inline-flex cursor-pointer items-center gap-2 rounded-xl border px-3 py-2 text-sm">
      <span>{loading ? "Uploading..." : "Upload file"}</span>
      <input
        type="file"
        accept=".txt,.pdf,text/plain,application/pdf"
        className="hidden"
        onChange={handleFileChange}
        disabled={loading}
      />
    </label>
  );
}
