async function checkHealth() {
  const res = await fetch("/api/health");
  const data = await res.json();

  document.getElementById("response").innerText = "API Status: " + data.status;
}
