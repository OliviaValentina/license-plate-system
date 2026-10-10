import { NextRequest, NextResponse } from "next/server";
import { AUTH_COOKIE, authServiceUrl, readTokenClaims } from "../../../auth/server";

/**
 * Exchanges AD credentials for a JWT via the auth-service and stores it in an
 * httpOnly cookie, so the token is never readable by browser JavaScript.
 */
export async function POST(request: NextRequest) {
  const url = authServiceUrl("/login/");
  if (!url) {
    return NextResponse.json(
      { detail: "AUTH_SERVICE_URL is not configured" },
      { status: 500 }
    );
  }

  const { username, password } = await request.json().catch(() => ({}));
  if (typeof username !== "string" || typeof password !== "string" || !username || !password) {
    return NextResponse.json({ detail: "Username and password are required" }, { status: 400 });
  }

  let upstreamResponse: Response;
  try {
    upstreamResponse = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username: username.trim(), password }),
      cache: "no-store",
    });
  } catch {
    return NextResponse.json({ detail: "Failed to reach auth-service" }, { status: 502 });
  }

  if (upstreamResponse.status === 401) {
    return NextResponse.json({ detail: "Invalid credentials" }, { status: 401 });
  }
  if (!upstreamResponse.ok) {
    return NextResponse.json({ detail: "Login is currently unavailable" }, { status: 502 });
  }

  const { access_token: token } = await upstreamResponse.json();
  // The auth-service puts the AD's own spelling of the username in the token.
  const { username: adUsername, exp } = readTokenClaims(token);

  const response = NextResponse.json({ username: adUsername ?? username.trim() });
  response.cookies.set(AUTH_COOKIE, token, {
    httpOnly: true,
    sameSite: "lax",
    secure: request.nextUrl.protocol === "https:",
    path: "/",
    ...(exp ? { expires: new Date(exp * 1000) } : {}),
  });
  return response;
}
