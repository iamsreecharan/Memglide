export interface Profile {
  user: string;
}

export async function authenticateUser(token: string): Promise<Profile> {
  const response = await fetch('/profile', {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error('Authentication failed');
  return response.json() as Promise<Profile>;
}
