import { NextRequest } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

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

  let body: { threadId?: string; replyId?: string; value?: number };
  try {
    body = await request.json();
  } catch {
    return Response.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const { threadId, replyId, value } = body;

  if (value !== 1 && value !== -1) {
    return Response.json(
      { error: "Value must be 1 or -1" },
      { status: 400 },
    );
  }

  if (!threadId && !replyId) {
    return Response.json(
      { error: "threadId or replyId required" },
      { status: 400 },
    );
  }

  if (threadId && replyId) {
    return Response.json(
      { error: "Provide threadId or replyId, not both" },
      { status: 400 },
    );
  }

  // --- Vote on a thread ---
  if (threadId) {
    const thread = await prisma.thread.findUnique({ where: { id: threadId } });
    if (!thread) {
      return Response.json({ error: "Thread not found" }, { status: 404 });
    }

    const existingVote = await prisma.vote.findUnique({
      where: { userId_threadId: { userId: user.id, threadId } },
    });

    if (existingVote) {
      if (existingVote.value === value) {
        // Same vote — remove it (toggle off)
        await prisma.$transaction([
          prisma.vote.delete({ where: { id: existingVote.id } }),
          prisma.thread.update({
            where: { id: threadId },
            data:
              value === 1
                ? { upvotes: { decrement: 1 } }
                : { downvotes: { decrement: 1 } },
          }),
        ]);
        return Response.json({ voted: null });
      } else {
        // Opposite vote — switch it
        await prisma.$transaction([
          prisma.vote.update({
            where: { id: existingVote.id },
            data: { value },
          }),
          prisma.thread.update({
            where: { id: threadId },
            data:
              value === 1
                ? { upvotes: { increment: 1 }, downvotes: { decrement: 1 } }
                : { upvotes: { decrement: 1 }, downvotes: { increment: 1 } },
          }),
        ]);
        return Response.json({ voted: value });
      }
    } else {
      // New vote
      await prisma.$transaction([
        prisma.vote.create({
          data: { value, userId: user.id, threadId },
        }),
        prisma.thread.update({
          where: { id: threadId },
          data:
            value === 1
              ? { upvotes: { increment: 1 } }
              : { downvotes: { increment: 1 } },
        }),
      ]);
      return Response.json({ voted: value });
    }
  }

  // --- Vote on a reply ---
  if (replyId) {
    const reply = await prisma.reply.findUnique({ where: { id: replyId } });
    if (!reply) {
      return Response.json({ error: "Reply not found" }, { status: 404 });
    }

    const existingVote = await prisma.vote.findUnique({
      where: { userId_replyId: { userId: user.id, replyId } },
    });

    if (existingVote) {
      if (existingVote.value === value) {
        // Same vote — remove it (toggle off)
        await prisma.$transaction([
          prisma.vote.delete({ where: { id: existingVote.id } }),
          prisma.reply.update({
            where: { id: replyId },
            data:
              value === 1
                ? { upvotes: { decrement: 1 } }
                : { downvotes: { decrement: 1 } },
          }),
        ]);
        return Response.json({ voted: null });
      } else {
        // Opposite vote — switch it
        await prisma.$transaction([
          prisma.vote.update({
            where: { id: existingVote.id },
            data: { value },
          }),
          prisma.reply.update({
            where: { id: replyId },
            data:
              value === 1
                ? { upvotes: { increment: 1 }, downvotes: { decrement: 1 } }
                : { upvotes: { decrement: 1 }, downvotes: { increment: 1 } },
          }),
        ]);
        return Response.json({ voted: value });
      }
    } else {
      // New vote
      await prisma.$transaction([
        prisma.vote.create({
          data: { value, userId: user.id, replyId },
        }),
        prisma.reply.update({
          where: { id: replyId },
          data:
            value === 1
              ? { upvotes: { increment: 1 } }
              : { downvotes: { increment: 1 } },
        }),
      ]);
      return Response.json({ voted: value });
    }
  }

  return Response.json({ error: "Unexpected error" }, { status: 500 });
}
