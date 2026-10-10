import { NextResponse } from "next/server";
import { AUTH_COOKIE } from "../../../auth/server";

export async function POST() {
  const response = NextResponse.json({ status: "ok" });
  response.cookies.delete(AUTH_COOKIE);
  return response;
}
