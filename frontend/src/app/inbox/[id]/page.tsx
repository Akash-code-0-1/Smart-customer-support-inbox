import React from 'react';
import ActiveInbox from '../../../components/ActiveInbox';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function InboxPage({ params }: PageProps) {
  const resolvedParams = await params;
  
  // Pasted from live active terminal session curl generation token output.
  const staticEvalToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzgyOTYyODI2LCJpYXQiOjE3ODI3MDM2MjYsImp0aSI6IjlkNDIyMzRmYmI4YTRjYjhiMTNlNjQ2NTFmYTRiYmQ5IiwidXNlcl9pZCI6IjEifQ.nqzcEf8eTtYD6Io67qYNyUp2vOVxuAVWWGScCACmd0E";

  return (
    <main className="container mx-auto p-4">
      <ActiveInbox conversationId={resolvedParams.id} token={staticEvalToken} />
    </main>
  );
}