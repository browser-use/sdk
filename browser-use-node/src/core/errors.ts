export class BrowserUseError extends Error {
  readonly statusCode: number;
  readonly detail: unknown;
  /** Integer-second Retry-After header, when the server sent one. */
  readonly retryAfter: number | undefined;

  constructor(statusCode: number, message: string, detail?: unknown, retryAfter?: number) {
    super(message);
    this.name = "BrowserUseError";
    this.statusCode = statusCode;
    this.detail = detail;
    this.retryAfter = retryAfter;
  }
}

/** Thrown on 402 when the API key's monthly spend limit is reached. */
export class APIKeySpendLimitError extends BrowserUseError {
  readonly code: string;
  readonly cap: number | undefined;
  readonly spent: number | undefined;

  constructor(
    message: string,
    detail: unknown,
    fields: { code: string; cap?: number; spent?: number },
    retryAfter?: number,
  ) {
    super(402, message, detail, retryAfter);
    this.name = "APIKeySpendLimitError";
    this.code = fields.code;
    this.cap = fields.cap;
    this.spent = fields.spent;
  }
}
