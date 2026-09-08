import { useCallback, useEffect, useState } from 'react';
import api from '../../services/api';
import type { ProfileAggregate } from './types';

/** Pulls a readable message out of an axios/FastAPI error. */
export const errorMessage = (error: any, fallback = 'Something went wrong. Please try again.'): string => {
  const detail = error?.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail) && detail.length) {
    const first = detail[0];
    const field = Array.isArray(first?.loc) ? first.loc[first.loc.length - 1] : '';
    return field ? `${field}: ${first.msg}` : first.msg || fallback;
  }
  if (error?.message === 'Network Error') return 'Cannot reach the server. Is the backend running?';
  return error?.message || fallback;
};

/**
 * Owns the profile aggregate. Every mutating endpoint returns the full
 * aggregate, so `save` just swaps state in — no refetch, no stale cards.
 */
export const useProfileData = () => {
  const [profile, setProfile] = useState<ProfileAggregate | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const { data } = await api.get<ProfileAggregate>('/profile');
      setProfile(data);
    } catch (error) {
      setLoadError(errorMessage(error, 'Could not load your profile.'));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  /** PUT/POST/DELETE a section endpoint and adopt the returned aggregate. */
  const save = useCallback(
    async (
      method: 'put' | 'post' | 'delete',
      path: string,
      body?: unknown,
    ): Promise<{ ok: boolean; message?: string }> => {
      try {
        const { data } =
          method === 'delete'
            ? await api.delete<ProfileAggregate>(path)
            : method === 'post'
              ? await api.post<ProfileAggregate>(path, body ?? {})
              : await api.put<ProfileAggregate>(path, body ?? {});

        // Section endpoints answer with the whole aggregate; guard anyway.
        if (data && typeof data === 'object' && 'completion' in data) {
          setProfile(data);
        } else {
          await load();
        }
        return { ok: true };
      } catch (error) {
        return { ok: false, message: errorMessage(error) };
      }
    },
    [load],
  );

  return { profile, loading, loadError, reload: load, save, setProfile };
};
