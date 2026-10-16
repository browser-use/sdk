import { readFile } from "fs/promises";
import { basename } from "path";
import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v4/types.js";

type ExtensionView = components["schemas"]["ExtensionView"];
type ExtensionListResponse = components["schemas"]["ExtensionListResponse"];

export interface ExtensionListParams {
  pageSize?: number;
  pageNumber?: number;
}

export class Extensions {
  constructor(private readonly http: HttpClient) {}

  /** Upload a Manifest V3 extension ZIP from a file path, Blob, or bytes. */
  async create(
    file: string | Blob | Uint8Array,
    extra: Record<string, string> = {},
  ): Promise<ExtensionView> {
    const form = new FormData();
    if (typeof file === "string") {
      form.append("file", new Blob([await readFile(file)]), basename(file));
    } else {
      form.append("file", file instanceof Blob ? file : new Blob([new Uint8Array(file)]), "extension.zip");
    }
    for (const [key, value] of Object.entries(extra)) form.append(key, value);
    return this.http.post<ExtensionView>("/extensions", form);
  }

  /** List uploaded extensions. */
  list(params?: ExtensionListParams): Promise<ExtensionListResponse> {
    return this.http.get<ExtensionListResponse>("/extensions", params as Record<string, unknown>);
  }

  /** Get an uploaded extension. */
  get(extensionId: string): Promise<ExtensionView> {
    return this.http.get<ExtensionView>(`/extensions/${extensionId}`);
  }

  /** Permanently delete an extension without affecting running browsers. */
  delete(extensionId: string): Promise<void> {
    return this.http.delete<void>(`/extensions/${extensionId}`);
  }
}
