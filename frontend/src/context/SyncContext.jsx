import React, { createContext, useContext, useState, useCallback, useRef } from "react";
import { streamSync } from "../api/insights";

const SyncContext = createContext();

export const useSync = () => useContext(SyncContext);

export function SyncProvider({ children }) {
  // Overall workflow state
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncStatus, setSyncStatus] = useState("idle"); // idle, processing, completed, error
  const [syncError, setSyncError] = useState("");
  const [totalMailsProcessed, setTotalMailsProcessed] = useState(0);

  // Modal visibility
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);

  // Mails and Extracted Data
  const [fetchedMails, setFetchedMails] = useState([]);
  const [extractedData, setExtractedData] = useState([]);

  // Stages
  const [stages, setStages] = useState([
    { id: "fetch_mails", title: "Fetch Mails", status: "pending" },
    { id: "extract_data", title: "Extract Mail Data", status: "pending" },
    { id: "categorize", title: "Categorize Expenses", status: "pending" },
    { id: "insights", title: "Generate Insights", status: "pending" },
  ]);

  // Keep track of cleanup function
  const cleanupRef = useRef(null);

  const startSync = useCallback(() => {
    if (isSyncing) return; // Prevent concurrent syncs

    setIsSyncing(true);
    setSyncStatus("processing");
    setSyncError("");
    setFetchedMails([]);
    setExtractedData([]);
    setTotalMailsProcessed(0);
    setIsDetailsModalOpen(true);

    // Reset stages
    setStages([
      { id: "fetch_mails", title: "Fetch Mails", status: "processing" },
      { id: "extract_data", title: "Extract Mail Data", status: "pending" },
      { id: "categorize", title: "Categorize Expenses", status: "pending" },
      { id: "insights", title: "Generate Insights", status: "pending" },
    ]);

    const updateStage = (id, status) => {
      setStages((prev) => prev.map((s) => (s.id === id ? { ...s, status } : s)));
    };

    cleanupRef.current = streamSync(
      (msg) => {
        if (msg.event === "mail_found") {
          setFetchedMails((prev) => [...prev, msg.data]);
        } else if (msg.event === "processing_started") {
          // This maps to internal nodes. We can map them to our high-level stages.
          const node = msg.data.node;
          if (node === "extract_transactions") {
            updateStage("fetch_mails", "completed");
            updateStage("extract_data", "processing");
          } else if (node === "analyze_spending" || node === "detect_recurring" || node === "validate_transactions") {
            updateStage("extract_data", "completed");
            updateStage("categorize", "processing");
          } else if (node === "generate_insights") {
            updateStage("categorize", "completed");
            updateStage("insights", "processing");
          }
        } else if (msg.event === "node_completed") {
          const node = msg.data.node;
          if (node === "extract_transactions") {
            if (msg.data.extracted_transactions) {
              setExtractedData(msg.data.extracted_transactions);
            }
          } else if (node === "generate_insights") {
            updateStage("insights", "completed");
          }
        }
      },
      (completedData) => {
        setSyncStatus("completed");
        setIsSyncing(false);
        setTotalMailsProcessed(completedData.total_mails || 0); // Need to refer to proper state or handle correctly
        
        // Ensure all stages are completed
        setStages((prev) => prev.map((s) => ({ ...s, status: "completed" })));
      },
      (errorData) => {
        console.error(errorData);
        setSyncStatus("error");
        setIsSyncing(false);
        setSyncError(typeof errorData === "string" ? errorData : "An error occurred");
        
        // Mark currently processing stages as failed
        setStages((prev) => prev.map((s) => (s.status === "processing" ? { ...s, status: "failed" } : s)));
      }
    );
  }, [isSyncing]);

  const closeDetailsModal = useCallback(() => {
    setIsDetailsModalOpen(false);
  }, []);

  const openDetailsModal = useCallback(() => {
    setIsDetailsModalOpen(true);
  }, []);

  // Optional: clear data
  const resetSyncState = useCallback(() => {
    setSyncStatus("idle");
    setFetchedMails([]);
    setExtractedData([]);
    setStages((prev) => prev.map((s) => ({ ...s, status: "pending" })));
  }, []);

  return (
    <SyncContext.Provider
      value={{
        isSyncing,
        syncStatus,
        syncError,
        totalMailsProcessed,
        isDetailsModalOpen,
        fetchedMails,
        extractedData,
        stages,
        startSync,
        closeDetailsModal,
        openDetailsModal,
        resetSyncState,
      }}
    >
      {children}
    </SyncContext.Provider>
  );
}
