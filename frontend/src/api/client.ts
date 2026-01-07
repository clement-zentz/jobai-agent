// SPDX-License-Identifier: AGPL-3.0-or-later
// File: frontend/src/api/client.ts

import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "/api",
  withCredentials: true,
});
