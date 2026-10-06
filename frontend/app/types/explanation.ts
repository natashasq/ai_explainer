export type SourceItem = {
  source: string;
  text: string;
};

export type ExplanationResponse = {
  answer: string;
  suggested_questions: string[];
  sources: SourceItem[];
};
