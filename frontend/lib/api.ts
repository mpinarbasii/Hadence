/**
 * Minimal typed client for the Hadence backend.
 *
 * Kept intentionally small — grows alongside backend endpoints as later
 * phases (Job Intelligence, Evidence Mapping, ...) land. No data-fetching
 * library is introduced until there's an actual caching/revalidation need.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export interface CareerProfile {
  id: string;
  user_id: string;
  display_name: string;
  skill_ids: string[];
}

export async function createProfile(userId: string, displayName: string): Promise<CareerProfile> {
  const res = await fetch(`${API_BASE_URL}/profiles`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, display_name: displayName }),
  });
  if (!res.ok) {
    throw new Error(`Failed to create profile: ${res.status}`);
  }
  return res.json();
}

export async function getProfile(profileId: string): Promise<CareerProfile> {
  const res = await fetch(`${API_BASE_URL}/profiles/${profileId}`);
  if (!res.ok) {
    throw new Error(`Failed to load profile: ${res.status}`);
  }
  return res.json();
}
