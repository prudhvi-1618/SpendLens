import client from "./client";

export const triggerSync = async () => {
  const { data } = await client.post("/insights/sync");
  return data;
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
