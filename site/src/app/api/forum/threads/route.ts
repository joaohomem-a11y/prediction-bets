import { NextRequest } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

const VALID_SECTIONS = [
  "signal-drop",
  "contrarian-takes",
  "prediction-battles",
  "reality-check",
  "edge-lab",
  "off-market",
];

const PAGE_SIZE = 20;

export async function GET(request: NextRequest) {
  const { searchParams } = request.nextUrl;
  const section = searchParams.get("section");
  const sort = searchParams.get("sort") ?? "new";
  const page = Math.max(1, parseInt(searchParams.get("page") ?? "1", 10));

  if (!section || !VALID_SECTIONS.includes(section)) {
    return Response.json(
      { error: "Invalid or missing section" },
      { status: 400 },
    );
  }

  let orderBy: Record<string, string> | Record<string, string>[];

  switch (sort) {
    case "top":
      orderBy = { upvotes: "desc" };
      break;
    case "hot":
      orderBy = [{ upvotes: "desc" }, { createdAt: "desc" }];
      break;
    case "new":
    default:
      orderBy = { createdAt: "desc" };
      break;
  }

  const threads = await prisma.thread.findMany({
    where: { section },
    orderBy,
    skip: (page - 1) * PAGE_SIZE,
    take: PAGE_SIZE,
    include: {
      author: { select: { id: true, name: true, image: true, role: true } },
      _count: { select: { replies: true } },
    },
  });

  return Response.json(threads);
}

export async function POST(request: NextRequest) {
  const session = await getServerSession(authOptions);
  if (!session?.user?.email) {
    return Response.json({ error: "Unauthorized" }, { status: 401 });
  }

  const user = await prisma.user.findUnique({
    where: { email: session.user.email },
  });
  if (!user) {
    return Response.json({ error: "User not found" }, { status: 401 });
  }

  let body: { title?: string; body?: string; section?: string };
  try {
    body = await request.json();
  } catch {
    return Response.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const { title, body: threadBody, section } = body;

  if (!title || !title.trim()) {
    return Response.json({ error: "Title is required" }, { status: 400 });
  }
  if (!threadBody || !threadBody.trim()) {
    return Response.json({ error: "Body is required" }, { status: 400 });
  }
  if (!section || !VALID_SECTIONS.includes(section)) {
    return Response.json({ error: "Invalid section" }, { status: 400 });
  }

  const thread = await prisma.thread.create({
    data: {
      title: title.trim(),
      body: threadBody.trim(),
      section,
      authorId: user.id,
    },
    include: {
      author: { select: { id: true, name: true, image: true, role: true } },
    },
  });

  return Response.json(thread, { status: 201 });
}
