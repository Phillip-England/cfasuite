import { expect, test } from "bun:test";

const BASE_URL = "http://localhost:8080";
const CONCURRENT_REQUESTS = 50; // Number of concurrent requests at a time
const TEST_DURATION = 5 * 1000; // 10 seconds in milliseconds

test(
  "Benchmark: Measure requests per second over 10 seconds to xerus",
  async () => {
    const startTime = performance.now();
    let completedRequests = 0;
    let failedRequests = 0;

    const sendRequest = async () => {
      while (performance.now() - startTime < TEST_DURATION) {
        try {
          const res = await fetch(`${BASE_URL}/`);
          if (res.status === 200) {
            completedRequests++;
          } else {
            failedRequests++;
          }
        } catch {
          failedRequests++;
        }
      }
    };

    // Start concurrent requests
    const requests = Array(CONCURRENT_REQUESTS).fill(null).map(sendRequest);
    await Promise.all(requests);

    const endTime = performance.now();
    const timeTaken = (endTime - startTime) / 1000; // Convert to seconds
    const rps = completedRequests / timeTaken;

    console.log(
      `Completed ${completedRequests} requests in ${timeTaken.toFixed(2)}s`,
    );
    console.log(`Requests per second: ${rps.toFixed(2)}`);
    console.log(`Failed requests: ${failedRequests}`);

    expect(failedRequests).toBe(0); // Ensure no requests failed
  },
  15000,
);
