import { useQuery } from "@tanstack/react-query";

import { fetchAuthSession } from "../../api/client";
import { queryKeys } from "../../queryClient";
import { HAL_CHAT_ALLOWED_ROLES } from "./halChatConstants";

function isUnauthorized(error: unknown): boolean {
  return (
    typeof error === "object" &&
    error !== null &&
    "status" in error &&
    typeof (error as { status: unknown }).status === "number" &&
    (error as { status: number }).status === 401
  );
}

function hasHalChatRole(roles: readonly string[]): boolean {
  return roles.some((role) => HAL_CHAT_ALLOWED_ROLES.has(role));
}

/**
 * HAL visibility inside the protected dashboard shell.
 * Uses verified session roles when available; falls back to AppShell-only gating otherwise.
 */
export function useHalChatAccess(): boolean {
  const { data, isError, error, isPending } = useQuery({
    queryKey: queryKeys.authSession,
    queryFn: fetchAuthSession,
    retry: false,
    staleTime: 60_000,
  });

  if (isPending) {
    return false;
  }

  if (isError) {
    return !isUnauthorized(error);
  }

  if (data.roles.length > 0) {
    return hasHalChatRole(data.roles);
  }

  return true;
}
