import type { NextConfig } from "next";
import { loadEnvConfig } from "@next/env";
import path from "path";

// Load environment variables from the parent directory (project root)
const projectRoot = path.join(process.cwd(), "..");
loadEnvConfig(projectRoot);

const nextConfig: NextConfig = {
  /* config options here */
};

export default nextConfig;
