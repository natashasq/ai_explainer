type ApiMessage = {
  role: "user" | "assistant";
  content: string;
};

export type UploadResponse = {
  knowledge_base_id: string;
  filename: string;
  chunk_count: number;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export async function explainFromMessages(
  messages: ApiMessage[],
  knowledgeBaseId: string,
) {
  const response = await fetch(`${API_BASE_URL}/api/explain`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ messages, knowledge_base_id: knowledgeBaseId }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || "Failed to fetch explanation");
  }

  return response.json();
}

export async function streamAnswerFromMessages(
  messages: ApiMessage[],
  knowledgeBaseId: string,
  onChunk: (chunk: string) => void,
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/explain-stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ messages, knowledge_base_id: knowledgeBaseId }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || "Failed to stream explanation");
  }

  if (!response.body) {
    throw new Error("ReadableStream not available");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value, { stream: true });
    onChunk(chunk);
  }
}

export async function uploadFile(file: File, existingKbId?: string): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  if (existingKbId) formData.append("existing_kb_id", existingKbId);

  const response = await fetch(`${API_BASE_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || "Failed to upload file");
  }

  return response.json();
}
