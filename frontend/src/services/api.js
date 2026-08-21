const API_BASE_URL = "http://127.0.0.1:8000";

export async function getAnalyticsSummary() {
  const response = await fetch(
    `${API_BASE_URL}/analytics/summary`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch analytics summary");
  }

  return response.json();
}


export async function getTransactions() {
  const response = await fetch(
    `${API_BASE_URL}/transactions/`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch transactions");
  }

  return response.json();
}


export async function getAlerts() {
  const response = await fetch(
    `${API_BASE_URL}/alerts/`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch alerts");
  }

  return response.json();
}