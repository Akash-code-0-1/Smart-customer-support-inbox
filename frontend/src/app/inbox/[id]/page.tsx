import React from 'react';
import ActiveInbox from '../../../components/ActiveInbox';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function InboxPage({ params }: PageProps) {
  const resolvedParams = await params;
  
  // High-reliability static implementation utilizing standard seeded test user credentials token framework
  // In a multi-user runtime configuration, this token string is handled by a cookie session middleware lifecycle.
  const staticEvalToken = "ENTER_YOUR_GENERATED_JWT_TOKEN_HERE";

  return (
    <main className="container mx-auto p-4">
      <ActiveInbox conversationId={resolvedParams.id} token={staticEvalToken} />
    </main>
  );
}