export { BrowserUse } from "./v4/client.js";
export type { BrowserUseOptions } from "./v4/client.js";

export { Browsers } from "./v4/resources/browsers.js";
export type { CreateBrowserBody } from "./v4/resources/browsers.js";

export { BrowserUseError } from "./core/errors.js";

export { Runs } from "./v4/resources/runs.js";
export type {
  RunCreateBody,
  RunListParams,
  RunEventsParams,
  WaitOptions,
} from "./v4/resources/runs.js";

export { Sessions } from "./v4/resources/sessions.js";
export type { SessionListParams } from "./v4/resources/sessions.js";

export { Workspaces } from "./v4/resources/workspaces.js";
export type { WorkspaceFilesParams } from "./v4/resources/workspaces.js";

export type { components as V4Types } from "./generated/v4/types.js";

// Re-export user-facing schema types so users never need to import from generated/.
import type { components } from "./generated/v4/types.js";
type S = components["schemas"];

// Run models
export type RunCreateRequest = S["RunCreateRequest"];
export type RunCreateResponse = S["RunCreateResponse"];
export type RunSummary = S["RunSummary"];
export type RunStatusResponse = S["RunStatusResponse"];
export type RunListResponse = S["RunListResponse"];
export type RunEvent = S["RunEvent"];
export type RunEventsResponse = S["RunEventsResponse"];
export type RunAttachment = S["RunAttachment"];
export type RunAttachmentsResponse = S["RunAttachmentsResponse"];
export type RunBrowserSettings = S["RunBrowserSettings"];
export type RunJudgeSettings = S["RunJudgeSettings"];
export type InlineSecretSource = S["InlineSecretSource"];
export type SecretBinding = S["SecretBinding"];

// Session models
export type BrowserSessionItemView = S["BrowserSessionItemView"];
export type BrowserSessionView = S["BrowserSessionView"];
export type SessionInfo = S["SessionInfo"];
export type SessionListResponse = S["SessionListResponse"];
export type QueueMessageRequest = S["QueueMessageRequest"];
export type QueuedMessage = S["QueuedMessage"];
export type QueueListResponse = S["QueueListResponse"];

// Workspace models
export type WorkspaceInfo = S["WorkspaceInfo"];
export type WorkspaceCreateRequest = S["WorkspaceCreateRequest"];
export type WorkspaceUpdateRequest = S["WorkspaceUpdateRequest"];
export type WorkspaceSizeInfo = S["WorkspaceSizeInfo"];
export type WorkspaceFileInfo = S["WorkspaceFileInfo"];
export type WorkspaceFileListResponse = S["WorkspaceFileListResponse"];
export type WorkspaceFileUploadItem = S["WorkspaceFileUploadItem"];
export type WorkspaceFileUploadRequest = S["WorkspaceFileUploadRequest"];
export type WorkspaceFileUploadResponse = S["WorkspaceFileUploadResponse"];
export type WorkspaceFileUploadResponseItem = S["WorkspaceFileUploadResponseItem"];

// Enums / string unions
export type ProxyCountryCode = S["ProxyCountryCode"];
export type CustomProxy = S["CustomProxy"];

/** Run status — terminal values are completed | failed | cancelled. */
export type RunStatus = S["RunStatusResponse"]["status"];
