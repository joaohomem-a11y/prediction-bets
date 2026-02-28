import { NextRequest } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;

  const replies = await prisma.reply.findMany({
    where: { threadId: id },
    include: {
      author: { select: { id: true, name: true, image: true, role: true } },
      _count: { select: { childReplies: true } },
    },
    orderBy: { createdAt: "asc" },
  });

  return Response.json(replies);
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
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

  const { id: threadId } = await params;

  const thread = await prisma.thread.findUnique({ where: { id: threadId } });
  if (!thread) {
    return Response.json({ error: "Thread not found" }, { status: 404 });
  }

  let body: { body?: string; parentReplyId?: string };
  try {
    body = await request.json();
  } catch {
    return Response.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const { body: replyBody, parentReplyId } = body;

  if (!replyBody || !replyBody.trim()) {
    return Response.json({ error: "Body is required" }, { status: 400 });
  }

  if (parentReplyId) {
    const parentReply = await prisma.reply.findUnique({
      where: { id: parentReplyId },
    });
    if (!parentReply || parentReply.threadId !== threadId) {
      return Response.json(
        { error: "Invalid parent reply" },
        { status: 400 },
      );
    }
  }

  const reply = await prisma.reply.create({
    data: {
      body: replyBody.trim(),
      authorId: user.id,
      threadId,
      parentReplyId: parentReplyId ?? null,
    },
    include: {
      author: { select: { id: true, name: true, image: true, role: true } },
    },
  });

  return Response.json(reply, { status: 201 });
}
