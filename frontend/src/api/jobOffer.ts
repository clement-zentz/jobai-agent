// SPDX-License-Identifier: AGPL-3.0-or-later
// File: frontend/src/api/jobOffer.ts

import { api } from "./client";
import type { JobOffer } from "../types/jobOffer";

export async function fetchJobOffers(): Promise<JobOffer[]> {
  const res = await api.get<JobOffer[]>("/job-offers/");
  return res.data;
}

// import { jobOffers } from "../mocks/jobOffers";

// export async function fetchJobOffers() {
//   return new Promise<typeof jobOffers>((resolve) => {
//     setTimeout(() => resolve(jobOffers), 1200) // fake latency
//   })
// }
