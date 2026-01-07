// SPDX-License-Identifier: AGPL-3.0-or-later
// File: frontend/src/pages/JobOffers.tsx

import { useEffect, useState } from "react";
import { fetchJobOffers } from "../api/jobOffer";
import type { JobOffer } from "../types/jobOffer";

export function JobOffers() {
  const [offers, setOffers] = useState<JobOffer[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchJobOffers()
      .then(setOffers)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading job offers...</p>;

  return (
    <div>
      <h1 className="text-3xl p-2 bg-amber-300">Job Offers</h1>
      <div
        className="
            grid grid-cols-[1fr_1fr_1fr_1fr]
            text-xl px-2 py-1 font-bold border"
      >
        <span>Title</span>
        <span>Company</span>
        <span>Location</span>
        <span>Platform</span>
      </div>
      <ul role="list" className="list-none text-gray-300">
        {offers.map((o) => (
          <li
            key={o.id}
            className="
                    grid grid-cols-[1fr_1fr_1fr_1fr]
                    px-2 py-1"
          >
            <span className="truncate">
              <strong>{o.title}</strong>
            </span>
            <span>{o.company}</span>
            <span>{o.location}</span>
            <span>{o.platform}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
