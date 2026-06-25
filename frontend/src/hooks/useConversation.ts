import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";

export interface Message {
  id?: number;
  sender: "customer" | "agent";
  message: string;
  created_at?: string;
}

interface ConversationData {
  lock_holder: string | null;
  is_locked_by_me: boolean;
  messages: Message[];
}

export function useConversation(conversationId: string, token: string) {
  const queryClient = useQueryClient();
  const [toast, setToast] = useState<string | null>(null);
  const cacheKey = ["conversation", conversationId];

  const { data } = useQuery<ConversationData>({
    queryKey: cacheKey,
    queryFn: async () => {
      const res = await fetch(
        `http://localhost:8000/api/conversations/${conversationId}/`,
        {
          headers: { Authorization: `Bearer ${token}` },
        },
      );
      if (!res.ok) throw new Error("Failed to load thread data");
      return res.json();
    },
  });

  useEffect(() => {
    // Standardizing Headers inside SSE Connection Framework via dynamic authentication validation paths
    const es = new EventSource(
      `http://localhost:8000/api/conversations/${conversationId}/stream/?token=${token}`,
    );

    es.addEventListener("message", (e: MessageEvent) => {
      const newMsg = JSON.parse(e.data);
      queryClient.setQueryData<ConversationData>(cacheKey, (old) => {
        if (!old) return old;
        if (
          old.messages.some(
            (m) => m.message === newMsg.message && m.sender === "agent",
          )
        )
          return old;
        return { ...old, messages: [...old.messages, newMsg] };
      });
    });

    es.addEventListener("lock_update", (e: MessageEvent) => {
      const lockData = JSON.parse(e.data);
      queryClient.setQueryData<ConversationData>(cacheKey, (old) => {
        if (!old) return old;
        return {
          ...old,
          lock_holder: lockData.lock_holder,
          is_locked_by_me: lockData.lock_holder === "admin@test.com",
        };
      });
    });

    return () => es.close();
  }, [conversationId, queryClient]);

  const mutation = useMutation({
    mutationFn: async (text: string) => {
      const response = await fetch(
        `http://localhost:8000/api/conversations/${conversationId}/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ message: text }),
        },
      );
      if (!response.ok) throw new Error(response.status.toString());
      return response.json();
    },
    onMutate: async (newMessageText) => {
      await queryClient.cancelQueries({ queryKey: cacheKey });
      const previousData = queryClient.getQueryData<ConversationData>(cacheKey);

      queryClient.setQueryData<ConversationData>(cacheKey, (old) => {
        if (!old) return old;
        const mockMsg: Message = {
          sender: "agent",
          message: newMessageText,
          created_at: new Date().toISOString(),
        };
        return { ...old, messages: [...old.messages, mockMsg] };
      });

      return { previousData };
    },
    onError: (err: Error, newMessageText, context) => {
      if (context?.previousData) {
        queryClient.setQueryData(cacheKey, context.previousData);
      }
      if (err.message === "423") {
        setToast("Action Failed: Thread is locked by another agent.");
      } else {
        setToast("Network Error: Failed to transmit message down pipeline.");
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: cacheKey });
    },
  });

  return {
    messages: data?.messages || [],
    lockHolder: data?.lock_holder || null,
    isLocked: data ? !data.is_locked_by_me : false,
    sendMessage: mutation.mutate,
    toast,
    clearToast: () => setToast(null),
  };
}
