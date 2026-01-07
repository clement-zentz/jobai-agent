// SPDX-License-Identifier: AGPL-3.0-or-later
// File: frontend/src/App.tsx

import { RouterProvider } from "react-router-dom";
import { router } from "./router";

function App() {
  return <RouterProvider router={router} />;
}

export default App;
