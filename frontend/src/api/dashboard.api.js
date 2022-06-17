import httpClient from "@/api/httpClient";
const ENDPOINT = "/aps";
const dispatchJob = (job) => httpClient.post(ENDPOINT + "/" + String(job));
const terminateJob = (job) => httpClient.delete(ENDPOINT + "/" + String(job));

export { dispatchJob, terminateJob };
