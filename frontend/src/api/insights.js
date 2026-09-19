import client from "./client";

export const triggerSync = async () => {
  const { data } = await client.post("/insights/sync");
  return data;
};

export const streamSync = (onMessage, onComplete, onError) => {
  // Use EventSource for Server-Sent Events
  const baseURL = client.defaults.baseURL || "http://localhost:8000";
  // The client usually uses standard paths, let's extract the base URL from the axios instance
  
  const eventSource = new EventSource(`${baseURL}/insights/sync/stream`, {
    withCredentials: true
  });

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      // The event stream passes event types manually or in the message payload
      // In our backend implementation, we use `event: eventName` natively, so standard .onmessage gets it if no specific event listener is added, 
      // but wait, EventSource triggers specific event listeners if `event:` is specified.
      // So we should add specific listeners.
    } catch (e) {
      console.error("Failed to parse SSE data", e);
    }
  };

  eventSource.addEventListener("processing_started", (e) => {
    onMessage({ event: "processing_started", data: JSON.parse(e.data) });
  });

  eventSource.addEventListener("mail_found", (e) => {
    onMessage({ event: "mail_found", data: JSON.parse(e.data) });
  });

  eventSource.addEventListener("node_completed", (e) => {
    onMessage({ event: "node_completed", data: JSON.parse(e.data) });
  });

  eventSource.addEventListener("processing_completed", (e) => {
    onComplete(JSON.parse(e.data));
    eventSource.close();
  });

  eventSource.addEventListener("error", (e) => {
    if (e.data) {
      try {
        onError(JSON.parse(e.data));
      } catch (err) {
        onError("Stream error occurred");
      }
    } else {
      onError("Connection closed unexpectedly");
    }
    eventSource.close();
  });

  return () => {
    eventSource.close(); // Cleanup function to close the stream
  };
};

export const fetchProfile = async () => {
  const { data } = await client.get("/insights/profile");
  return data;
};

export const fetchAnomalies = async () => {
  const { data } = await client.get("/insights/anomalies");
  return data;
};

export const fetchTransactions = async (params) => {
  const { data } = await client.get("/insights/transactions", { params });
  return data;
};

export const fetchEmailStatus = async () => {
  const { data } = await client.get("/emails/status");
  return data;
};

export const triggerEmailSync = async () => {
  const { data } = await client.post("/emails/sync");
  return data;
};
