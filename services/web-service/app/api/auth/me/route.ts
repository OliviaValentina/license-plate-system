import { NextResponse } from "next/server";
import { getCurrentUser } from "../../../auth/server";

export async function GET() {
  const user = await getCurrentUser();
  if (!user) {
    return NextResponse.json({ detail: "Not logged in" }, { status: 401 });
  }
  return NextResponse.json(user);
}
