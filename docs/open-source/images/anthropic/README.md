# Anthropic integration diagrams

`architecture.svg` introduces the integration. `tool-sequence.svg` follows a browser call and a Bash call through the tool runner. Both have an editable Excalidraw scene with embedded logo assets and SVG exports with accessible titles and descriptions. The warm background is part of each illustration and works in either docs theme. Keep the text explanations in the MDX page alongside the diagrams.

Sources:

- Anthropic mark: navigation SVG from https://www.anthropic.com/, retrieved 2026-10-01. Original geometry retained.
- Browser Use wordmark: this repository's `docs/logo/light.svg` at d76a854818dec1d8ec418484043731c9ed76c77b. Original paths and aspect ratio retained.
- Editable format follows the existing `docs/cloud/images/*.excalidraw` convention.

Bash is shown with the Browser Use tools. It executes on the SDK host. The 31-action count refers to browser actions only.

`confirmation-callback.svg` follows a single file upload through validation, approval, and execution or refusal. `files-between-hosts.svg` separates application-supplied byte transfers from document IDs, file paths, and download notifications. Their editable Excalidraw scenes accompany the SVGs. Bash remains in the Browser Use integration; browser confirmation does not apply to Bash.
