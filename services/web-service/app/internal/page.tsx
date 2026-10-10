import { redirect } from "next/navigation";
import { getCurrentUser } from "../auth/server";
import { InternalContent } from "./InternalContent";

// The session must be checked on every request, never served from a cache.
export const dynamic = "force-dynamic";

export default async function InternalPage() {
  const user = await getCurrentUser();
  if (!user) {
    redirect("/login?next=/internal");
  }

  return <InternalContent username={user.username} />;
}
