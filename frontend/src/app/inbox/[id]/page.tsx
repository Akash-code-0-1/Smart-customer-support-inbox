import React from 'react';
import ActiveInbox from '../../../components/ActiveInbox';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function InboxPage({ params }: PageProps) {
  const resolvedParams = await params;
  
  // Pasted from live active terminal session curl generation token output.
  const staticEvalToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzgyMzgzNjUzLCJpYXQiOjE3ODIzNzY0NTMsImp0aSI6ImE4MzMxZTFhY2QyODRiM2I5YzliMDBlYWU2ZGQ4NDExIiwidXNlcl9pZCI6IjEifQ.Opfnf73PdHNtU1l_DNrmk7iKnlaZDQbleV9KQ4t_5tg";

  return (
    <main className="container mx-auto p-4">
      <ActiveInbox conversationId={resolvedParams.id} token={staticEvalToken} />
    </main>
  );
}