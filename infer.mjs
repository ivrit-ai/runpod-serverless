# Simple reference code for infering using Javascript

import runpodSdk from "runpod-sdk";

const { RUNPOD_API_KEY, ENDPOINT_ID } = process.env;

const runpod = runpodSdk(RUNPOD_API_KEY);
const endpoint = runpod.endpoint(ENDPOINT_ID);

const result = await endpoint.runSync({ "input" : {
  "type" : "url",
  "url" : "https://github.com/metaldaniel/HebrewASR-Comparison/raw/main/HaTankistiot_n12-mp3.mp3"
} });

console.log(result);

