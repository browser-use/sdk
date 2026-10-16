export { BrowserUse } from "./v4/client.js";
export type { BrowserUseOptions } from "./v4/client.js";

export { Browsers } from "./v4/resources/browsers.js";
export type {
  BrowserDownloadsParams,
  BrowserListParams,
  CreateBrowserBody,
} from "./v4/resources/browsers.js";

export { Profiles } from "./v4/resources/profiles.js";
export type { ProfileListParams } from "./v4/resources/profiles.js";

export { APIKeySpendLimitError, BrowserUseError } from "./core/errors.js";

export { Extensions } from "./v4/resources/extensions.js";
export type { ExtensionListParams } from "./v4/resources/extensions.js";

export { Runs } from "./v4/resources/runs.js";
export type {
  RunCreateBody,
  RunModel,
  RunListParams,
  RunEventsParams,
  WaitOptions,
} from "./v4/resources/runs.js";

export { Sessions } from "./v4/resources/sessions.js";
export type { SendMessageOptions, SessionListParams } from "./v4/resources/sessions.js";

export { Workspaces } from "./v4/resources/workspaces.js";
export type { WorkspaceFilesParams } from "./v4/resources/workspaces.js";

export { Integrations } from "./v4/resources/integrations.js";
export type { IntegrationListParams } from "./v4/resources/integrations.js";

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
export type OnePasswordSecretSource = S["OnePasswordSecretSource"];
export type SecretBinding = S["SecretBinding"];

// Browser models
export type BrowserSessionItemView = S["BrowserSessionItemView"];
export type BrowserSessionView = S["BrowserSessionView"];
export type BrowserSessionListResponse = S["BrowserSessionListResponse"];
export type BrowserSessionStatus = S["BrowserSessionStatus"];
export type BrowserDownloadFile = S["BrowserDownloadFile"];
export type BrowserDownloadListResponse = S["BrowserDownloadListResponse"];

// Profile models
export type ProfileView = S["ProfileView"];
export type ProfileListResponse = S["ProfileListResponse"];
export type ProfileCreateRequest = S["ProfileCreateRequest"];
export type ProfileUpdateRequest = S["ProfileUpdateRequest"];

// Session models
export type SessionInfo = S["SessionInfo"];
export type SessionListResponse = S["SessionListResponse"];
export type QueueMessageRequest = S["QueueMessageRequest"];
export type QueuedMessage = S["QueuedMessage"];
export type QueueListResponse = S["QueueListResponse"];
export type SessionUpdateRequest = S["SessionUpdateRequest"];
export type SessionCostResponse = S["SessionCostResponse"];
export type SessionCostCapRequest = S["SessionCostCapRequest"];
export type SessionCostCapResponse = S["SessionCostCapResponse"];
export type SessionShareInfo = S["SessionShareInfo"];
export type SessionShareUpdateRequest = S["SessionShareUpdateRequest"];

// Integration models
export type IntegrationListResponse = S["IntegrationListResponse"];
export type IntegrationResponse = S["IntegrationResponse"];
export type IntegrationCategoryResponse = S["IntegrationCategoryResponse"];
export type AuthorizeResponse = S["AuthorizeResponse"];
export type ConnectionStatusResponse = S["ConnectionStatusResponse"];
export type DisconnectResponse = S["DisconnectResponse"];

// Errors
export type APIKeySpendLimitDetail = S["APIKeySpendLimitDetail"];

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

// Extension models
export type BrowserExtensionView = S["BrowserExtensionView"];
export type ExtensionView = S["ExtensionView"];
export type ExtensionListResponse = S["ExtensionListResponse"];

// Enums / string unions
export type ProxyCountryCode = S["ProxyCountryCode"];
export type CustomProxy = S["CustomProxy"];

/** Run status — terminal values are completed | failed | cancelled. */
export type RunStatus = S["RunStatusResponse"]["status"];
