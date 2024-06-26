export const API_BASE_URL = process.env.VUE_APP_API_BASE_URL

export const SERVER_BASE_URL = process.env.VUE_APP_SERVER_BASE_URL

export const chipsContent = [
  { statement: "Any grammar issues here?", template: "[YOUR INPUT]" },
  { statement: "Is this git commit ok?", template: "[YOUR INPUT]" },
  { statement: "Git commit and grammar ok?", template: "[YOUR INPUT]" },
  { statement: "Translate to [LANGUAGE]", template: "[YOUR INPUT]" },
  {
    statement: "Check this email and suggest any possible changes",
    template: "[YOUR EMAIL]",
  },
  {
    statement: "Extract a summary from the following text",
    template: "[YOUR INPUT]",
  },
  { statement: "Tell me a story", template: "" },
  {
    statement: "Analyze this code and give me a summary feedback",
    template: "[YOUR CODE]",
  },
  {
    statement: "Analyze this code and list possible bugs",
    template: "[YOUR CODE]",
  },
];
