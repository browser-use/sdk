export class BrowserUseError extends Error {
  readonly statusCode: number;
  readonly detail: unknown;

  constructor(statusCode: number, message: string, detail?: unknown) {
    super(message);
    this.name = "BrowserUseError";
    this.statusCode = statusCode;
    this.detail = detail;
  }
}
