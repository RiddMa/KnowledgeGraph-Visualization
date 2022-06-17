import httpClient from "@/api/httpClient";
const sendHeartBeat = () => httpClient.get("/heartbeat");

export { sendHeartBeat };
