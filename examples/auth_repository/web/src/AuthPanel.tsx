import { useState } from 'react';
import { authenticateUser } from './auth';
import { useFeatureFlag } from './missingFeatureFlags';

export function AuthPanel() {
  const [user, setUser] = useState<string | null>(null);
  const enabled = useFeatureFlag('profile');
  async function loadProfile() {
    const profile = await authenticateUser('');
    setUser(profile.user);
  }
  return <section><button disabled={!enabled} onClick={loadProfile}>Load profile</button><p>{user}</p></section>;
}
