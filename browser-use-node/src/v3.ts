export { BrowserUse } from "./v3/client.js";
export type { BrowserUseOptions, RunSessionOptions } from "./v3/client.js";

export { BrowserUseError } from "./core/errors.js";

export { SessionRun } from "./v3/helpers.js";
export type { RunOptions, SessionResult } from "./v3/helpers.js";

export { Sessions } from "./v3/resources/sessions.js";
export type { CreateSessionBody, SessionListParams, SessionFilesParams } from "./v3/resources/sessions.js";

export type { components as V3Types } from "./generated/v3/types.js";

// Re-export user-facing schema types so users never need to import from generated/.
import type { components } from "./generated/v3/types.js";
type S = components["schemas"];

// Response models
export type SessionResponse = S["SessionResponse"];
export type SessionListResponse = S["SessionListResponse"];
export type FileListResponse = S["FileListResponse"];
export type FileInfo = S["FileInfo"];

// Input / request models
export type RunTaskRequest = S["RunTaskRequest"];

// Enums / string unions
export type BuAgentSessionStatus = S["BuAgentSessionStatus"];
export type BuModel = S["BuModel"];
export type ProxyCountryCode = S["ProxyCountryCode"];
