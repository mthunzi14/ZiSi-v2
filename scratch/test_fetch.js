const marketId = "59968297620348410202176423560807727738109914447470562872263967326570969891563";

async function testFetch() {
  const start = Date.now();
  try {
    const url = `https://clob.polymarket.com/book?token_id=${marketId}`;
    console.log("Fetching:", url);
    const r = await fetch(url);
    console.log("Response status:", r.status, "took", Date.now() - start, "ms");
    if (!r.ok) {
      console.log("Response not ok");
      return;
    }
    const d = await r.json();
    console.log("Data structure:", JSON.stringify(d, null, 2).slice(0, 500));
  } catch (err) {
    console.error("Error:", err);
  }
}

testFetch();
