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
      <ul className="list-none text-gray-300">
        <div
          className="
                grid grid-cols-[1fr_1fr_1fr_1fr]
                text-xl p-2 font-bold border"
        >
          <div>Title</div>
          <div>Company</div>
          <div>Location</div>
          <div>Platform</div>
        </div>
        {offers.map((o) => (
          <li
            key={o.id}
            className="
                    grid grid-cols-[1fr_1fr_1fr_1fr] mb-2 pl-2"
          >
            <div className="truncate">
              <strong>{o.title}</strong>
            </div>
            <div>{o.company}</div>
            <div>{o.location}</div>
            <div>{o.platform}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}
