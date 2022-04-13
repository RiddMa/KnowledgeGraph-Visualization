import axios from "axios";

const httpClient = axios.create({
  baseURL: process.env.VUE_APP_BASE_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
    // anything you want to add to the headers
  },
});

export default httpClient;
