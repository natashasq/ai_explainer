export type SourceItem = {
  source: string;
  text: string;
};

export type SourcePreviewProps = {
  source: string;
  text: string;
  previewLength?: number;
};

export type UserMessage = {
  id: string;
  role: "user";
  content: string;
};

export type AssistantMessage = {
  id: string;
  role: "assistant";
  content: string;
  suggestedQuestions: string[];
  sources: SourceItem[];
};

export type ChatMessage = UserMessage | AssistantMessage;

export type ChatSession = {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: string;
  updatedAt: string;
  knowledgeBaseId: string;
  knowledgeBaseLabel: string;
};
