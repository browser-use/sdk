export { BrowserUse } from "./v2/client.js";
export type { BrowserUseOptions, RunTaskOptions } from "./v2/client.js";

export { BrowserUseError } from "./core/errors.js";

export { TaskRun } from "./v2/helpers.js";
export type { TaskResult, RunOptions } from "./v2/helpers.js";

export { Billing } from "./v2/resources/billing.js";
export { Tasks } from "./v2/resources/tasks.js";
export type { CreateTaskBody, TaskListParams } from "./v2/resources/tasks.js";
export { Sessions } from "./v2/resources/sessions.js";
export type { SessionListParams } from "./v2/resources/sessions.js";
export { Files } from "./v2/resources/files.js";
export { Profiles } from "./v2/resources/profiles.js";
export type { ProfileListParams } from "./v2/resources/profiles.js";
export { Browsers } from "./v2/resources/browsers.js";
export type { BrowserListParams } from "./v2/resources/browsers.js";
export { Skills } from "./v2/resources/skills.js";
export type { SkillListParams, SkillExecutionListParams } from "./v2/resources/skills.js";
export { Marketplace } from "./v2/resources/marketplace.js";
export type { MarketplaceListParams } from "./v2/resources/marketplace.js";

export type { components as V2Types } from "./generated/v2/types.js";

// Re-export user-facing schema types so users never need to import from generated/.
import type { components } from "./generated/v2/types.js";
type S = components["schemas"];

// Response models
export type AccountView = S["AccountView"];
export type BrowserSessionItemView = S["BrowserSessionItemView"];
export type BrowserSessionListResponse = S["BrowserSessionListResponse"];
export type BrowserSessionView = S["BrowserSessionView"];
export type CreateSkillResponse = S["CreateSkillResponse"];
export type ExecuteSkillResponse = S["ExecuteSkillResponse"];
export type FileView = S["FileView"];
export type MarketplaceSkillListResponse = S["MarketplaceSkillListResponse"];
export type MarketplaceSkillResponse = S["MarketplaceSkillResponse"];
export type ParameterSchema = S["ParameterSchema"];
export type PlanInfo = S["PlanInfo"];
export type ProfileListResponse = S["ProfileListResponse"];
export type ProfileView = S["ProfileView"];
export type RefineSkillResponse = S["RefineSkillResponse"];
export type SessionItemView = S["SessionItemView"];
export type SessionListResponse = S["SessionListResponse"];
export type SessionView = S["SessionView"];
export type ShareView = S["ShareView"];
export type SkillExecutionListResponse = S["SkillExecutionListResponse"];
export type SkillExecutionOutputResponse = S["SkillExecutionOutputResponse"];
export type SkillExecutionView = S["SkillExecutionView"];
export type SkillListResponse = S["SkillListResponse"];
export type SkillResponse = S["SkillResponse"];
export type TaskCreatedResponse = S["TaskCreatedResponse"];
export type TaskListResponse = S["TaskListResponse"];
export type TaskLogFileResponse = S["TaskLogFileResponse"];
export type TaskOutputFileResponse = S["TaskOutputFileResponse"];
export type TaskStatusView = S["TaskStatusView"];
export type TaskStepView = S["TaskStepView"];
export type TaskView = S["TaskView"];
export type UploadFilePresignedUrlResponse = S["UploadFilePresignedUrlResponse"];

// Input / request models
export type CreateBrowserSessionRequest = S["CreateBrowserSessionRequest"];
export type CreateSessionRequest = S["CreateSessionRequest"];
export type CreateSkillRequest = S["CreateSkillRequest"];
export type CreateTaskRequest = S["CreateTaskRequest"];
export type CustomProxy = S["CustomProxy"];
export type ExecuteSkillRequest = S["ExecuteSkillRequest"];
export type ProfileCreateRequest = S["ProfileCreateRequest"];
export type ProfileUpdateRequest = S["ProfileUpdateRequest"];
export type RefineSkillRequest = S["RefineSkillRequest"];
export type SessionSettings = S["SessionSettings"];
export type UpdateSkillRequest = S["UpdateSkillRequest"];
export type UploadFileRequest = S["UploadFileRequest"];
