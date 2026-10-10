import { cookies } from "next/headers";

export const AUTH_COOKIE = "lps-token";

export interface AuthUser {
  username: string;
}

/**
 * Builds a URL on the auth-service. Kept server-side so the internal
 * service URL never has to be exposed to the browser.
 */
export function authServiceUrl(path: string): string | null {
  const base = process.env.AUTH_SERVICE_URL;
  if (!base) return null;
  return `${base}/auth/v1${path}`;
}

/**
 * Returns the logged-in user by validating the session cookie's JWT against
 * the auth-service, or null if there is no valid session.
 */
export async function getCurrentUser(): Promise<AuthUser | null> {
  const token = (await cookies()).get(AUTH_COOKIE)?.value;
  const url = authServiceUrl("/login/me");
  if (!token || !url) return null;

  try {
    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
    if (!res.ok) return null;
    const data = await res.json();
    return { username: data.username };
  } catch {
    return null;
  }
}

/**
 * Reads the claims of a JWT without verifying it. Only use this on tokens just
 * received from the auth-service, never to decide whether a user is logged in.
 */
export function readTokenClaims(token: string): { username?: string; exp?: number } {
  try {
    return JSON.parse(Buffer.from(token.split(".")[1], "base64url").toString("utf-8"));
  } catch {
    return {};
  }
}
