import type { ChatModelAdapter } from "@assistant-ui/react";

import { HAL_MOCK_ASSISTANT_RESPONSE } from "./halChatConstants";
import type { HalPageContext } from "./useHalPageContext";

const MOCK_RESPONSE_DELAY_MS = 650;

function delay(ms: number, abortSignal: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    const timer = window.setTimeout(resolve, ms);
    const onAbort = () => {
      window.clearTimeout(timer);
      reject(new DOMException("Aborted", "AbortError"));
    };
    if (abortSignal.aborted) {
      onAbort();
      return;
    }
    abortSignal.addEventListener("abort", onAbort, { once: true });
  });
}

export function createHalMockChatAdapter(getPageContext: () => HalPageContext): ChatModelAdapter {
  return {
    async run({ abortSignal }) {
      // Reserved for future backend context attachment — kept local only for now.
      void getPageContext();

      await delay(MOCK_RESPONSE_DELAY_MS, abortSignal);

      return {
        content: [{ type: "text", text: HAL_MOCK_ASSISTANT_RESPONSE }],
      };
    },
  };
}
