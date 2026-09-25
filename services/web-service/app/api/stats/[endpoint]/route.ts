import { NextRequest, NextResponse } from "next/server";

const ALLOWED_ENDPOINTS = new Set([
  "duration-of-stay",
  "rush-hour",
  "monthly-trends",
  "weekday-trends",
  "visit-trends",
  "filter-options",
]);

/**
 * Proxies chart data requests to the analytics-service so the internal
 * service URL never has to be exposed to the browser.
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ endpoint: string }> }
) {
  const { endpoint } = await params;

  if (!ALLOWED_ENDPOINTS.has(endpoint)) {
    return NextResponse.json({ detail: "Unknown endpoint" }, { status: 404 });
  }

  const analyticsServiceUrl = process.env.ANALYTICS_SERVICE_URL;
  if (!analyticsServiceUrl) {
    return NextResponse.json(
      { detail: "ANALYTICS_SERVICE_URL is not configured" },
      { status: 500 }
    );
  }

  const search = request.nextUrl.search;
  const upstreamUrl = `${analyticsServiceUrl}/api/stats/${endpoint}${search}`;

  try {
    const upstreamResponse = await fetch(upstreamUrl, {
      cache: "no-store",
    });
    const body = await upstreamResponse.text();

    return new NextResponse(body, {
      status: upstreamResponse.status,
      headers: { "Content-Type": "application/json" },
    });
  } catch {
    return NextResponse.json(
      { detail: "Failed to reach analytics-service" },
      { status: 502 }
    );
  }
}

export async function POST(
  _request: NextRequest,
  { params }: { params: Promise<{ endpoint: string }> }
) {
  const { endpoint } = await params;

  if (endpoint !== "refresh") {
    return NextResponse.json({ detail: "Unknown endpoint" }, { status: 404 });
  }

  const analyticsServiceUrl = process.env.ANALYTICS_SERVICE_URL;
  if (!analyticsServiceUrl) {
    return NextResponse.json(
      { detail: "ANALYTICS_SERVICE_URL is not configured" },
      { status: 500 }
    );
  }

  try {
    const upstreamResponse = await fetch(`${analyticsServiceUrl}/api/stats/refresh`, {
      method: "POST",
      cache: "no-store",
    });
    const body = await upstreamResponse.text();

    return new NextResponse(body, {
      status: upstreamResponse.status,
      headers: { "Content-Type": "application/json" },
    });
  } catch {
    return NextResponse.json(
      { detail: "Failed to reach analytics-service" },
      { status: 502 }
    );
  }
}
