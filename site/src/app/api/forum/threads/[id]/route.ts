import { NextRequest } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;

  const thread = await prisma.thread.findUnique({
    where: { id },
    include: {
      author: { select: { id: true, name: true, image: true } },
      replies: {
        include: {
          author: { select: { id: true, name: true, image: true } },
          _count: { select: { childReplies: true } },
        },
        orderBy: { createdAt: "asc" },
      },
      _count: { select: { replies: true } },
    },
  });

  if (!thread) {
    return Response.json({ error: "Thread not found" }, { status: 404 });
  }

  return Response.json(thread);
}
