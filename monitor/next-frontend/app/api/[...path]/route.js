import { NextResponse } from "next/server";

async function proxy(request, { params }) {
  const base = process.env.MONITOR_API_URL?.replace(/\/+$/, "");
  if (!base || !(base.startsWith("https://") || base.startsWith("http://"))) {
    return NextResponse.json({ error: "감시 API 주소가 설정되지 않았습니다." }, { status: 503 });
  }
  const { path } = await params;
  const target = base + "/api/" + path.map(encodeURIComponent).join("/") + new URL(request.url).search;
  const headers = new Headers();
  for (const key of ["cookie", "x-csrf-token", "content-type"]) {
    const value = request.headers.get(key);
    if (value) headers.set(key, value);
  }
  try {
    const response = await fetch(target, {
      method: request.method,
      headers,
      body: ["GET", "HEAD"].includes(request.method) ? undefined : await request.arrayBuffer(),
      cache: "no-store",
      redirect: "manual",
    });
    const outgoing = new Headers();
    const contentType = response.headers.get("content-type");
    if (contentType) outgoing.set("content-type", contentType);
    const cookies = response.headers.getSetCookie?.() ?? [];
    for (const cookie of cookies) outgoing.append("set-cookie", cookie);
    return new NextResponse(response.body, { status: response.status, headers: outgoing });
  } catch {
    return NextResponse.json({ error: "감시 API에 연결하지 못했습니다. 잠시 후 다시 시도해 주세요." }, { status: 502 });
  }
}
export { proxy as GET, proxy as POST, proxy as PUT, proxy as PATCH, proxy as DELETE };
