import { NextRequest } from "next/server";
import { prisma } from "@/lib/prisma";
import { translateThread, translateReply } from "@/lib/translate";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  const locale = request.nextUrl.searchParams.get("locale") ?? "en";

  const thread = await prisma.thread.findUnique({
    where: { id },
    include: {
      author: { select: { id: true, name: true, image: true, role: true } },
      replies: {
        include: {
          author: { select: { id: true, name: true, image: true, role: true } },
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

  const translatedThread = translateThread(thread, locale);
  const translatedReplies = thread.replies.map((r) => {
    const tr = translateReply(r, locale);
    const { translations: _t, ...rest } = tr;
    return rest;
  });

  const { translations: _t, ...threadRest } = translatedThread;
  return Response.json({ ...threadRest, replies: translatedReplies });
}
