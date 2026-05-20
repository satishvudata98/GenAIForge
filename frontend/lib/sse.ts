"use client";

export type SseEventType = "chunk" | "source" | "meta" | "done";

export interface SseEvent {
  type: SseEventType;
  content?: unknown;
  index?: number;
}

export interface SseHandlers {
  onChunk?: (content: unknown, index?: number) => void;
  onSource?: (content: unknown) => void;
  onMeta?: (content: unknown) => void;
  onDone?: () => void;
  onError?: (err: Error) => void;
}

/**
 * Opens an SSE stream to a POST endpoint and dispatches events to handlers.
 * Returns an AbortController so the caller can cancel the stream.
 */
export function streamPost(url: string, body: unknown, handlers: SseHandlers): AbortController {
  const controller = new AbortController();

  (async () => {
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        signal: controller.signal,
      });

      if (!res.ok || !res.body) {
        handlers.onError?.(new Error(`HTTP ${res.status}: ${res.statusText}`));
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const lines = buffer.split("\n\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith("data: ")) continue;
          try {
            const event: SseEvent = JSON.parse(trimmed.slice(6));
            switch (event.type) {
              case "chunk":
                handlers.onChunk?.(event.content, event.index);
                break;
              case "source":
                handlers.onSource?.(event.content);
                break;
              case "meta":
                handlers.onMeta?.(event.content);
                break;
              case "done":
                handlers.onDone?.();
                return;
            }
          } catch {
            // malformed event — skip
          }
        }
      }
    } catch (err) {
      if ((err as Error).name !== "AbortError") {
        handlers.onError?.(err as Error);
      }
    }
  })();

  return controller;
}
