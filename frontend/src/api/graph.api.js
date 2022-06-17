import httpClient from "@/api/httpClient";
const ENDPOINT = "/graph";
const getGraphStats = () => httpClient.get(ENDPOINT);
const getGraphData = (limit) => httpClient.get(ENDPOINT + "/" + String(limit));
const getGraphSearch = (keyword) =>
  httpClient.get(ENDPOINT + "/search/" + keyword);

const getSampleData = (url) => httpClient.get(url);

export {
  getGraphStats,
  getGraphData,
  getGraphSearch,
  getSampleData,
};
