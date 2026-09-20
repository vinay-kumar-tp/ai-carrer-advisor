/** Mirrors the payloads returned by /api/events/*. */

export type EventType =
  | 'hackathon'
  | 'webinar'
  | 'workshop'
  | 'career_fair'
  | 'bootcamp'
  | 'tech_talk'
  | 'ama'
  | 'contest'
  | 'info_session'
  | 'diversity'
  | 'ideathon'
  | 'certification'
  | 'mock_interview'
  | 'conference'
  | 'internship_drive';

export type EventQuestion = {
  key: string;
  label: string;
  type: 'text' | 'textarea' | 'number' | 'select' | 'multiselect' | 'boolean' | 'url' | 'date';
  required?: boolean;
  options?: string[];
  placeholder?: string;
  help?: string;
};

export type AgendaItem = { time: string; title: string; detail: string };
export type Speaker = { name: string; title: string; company: string };

export type EventCard = {
  id: string;
  slug: string | null;
  title: string;
  description: string;
  event_type: EventType;
  mode: 'Online' | 'In Person' | 'Hybrid';
  event_date: string;
  end_date: string | null;
  timezone_label: string;
  duration_minutes: number | null;
  registration_deadline: string | null;
  location: string;
  venue: string;
  city: string;
  event_url: string | null;
  host_company: string;
  host_domain: string;
  host_logo: string;
  host_tagline: string;
  capacity: number | null;
  seats_taken: number;
  seats_left: number | null;
  price: number;
  currency: string;
  is_certified: boolean;
  is_featured: boolean;
  tags: string[];
  registered: boolean;
  registration_status: string | null;
  is_full: boolean;
  is_past: boolean;
};

export type EventDetail = EventCard & {
  about: string;
  agenda: AgendaItem[];
  speakers: Speaker[];
  prizes: string[];
  perks: string[];
  eligibility: string[];
  registration_questions: EventQuestion[];
  prefill: Record<string, any>;
};

export type EventListResponse = {
  items: EventCard[];
  total: number;
  skip: number;
  limit: number;
};

export type FacetCount = { name: string; count: number };

export type EventFacets = {
  event_types: FacetCount[];
  modes: FacetCount[];
  hosts: FacetCount[];
  cities: FacetCount[];
  total: number;
};

export type MyRegistration = {
  registration_id: string;
  ticket_code: string;
  status: string;
  registered_at: string;
  event: EventCard;
};

export type EventFilters = {
  keyword: string;
  event_type: string;
  mode: string;
  host: string;
  city: string;
  price: string;
  sort: string;
};

export const EMPTY_FILTERS: EventFilters = {
  keyword: '',
  event_type: '',
  mode: '',
  host: '',
  city: '',
  price: '',
  sort: 'soonest',
};

/** Human labels + a pastel tone per event format. */
export const EVENT_TYPE_META: Record<EventType, { label: string; tone: string; icon: string }> = {
  hackathon: { label: 'Hackathon', tone: 'violet', icon: '⚡' },
  webinar: { label: 'Webinar', tone: 'blue', icon: '🎧' },
  workshop: { label: 'Workshop', tone: 'mint', icon: '🛠️' },
  career_fair: { label: 'Career Fair', tone: 'peach', icon: '🤝' },
  bootcamp: { label: 'Bootcamp', tone: 'rose', icon: '🚀' },
  tech_talk: { label: 'Tech Talk', tone: 'blue', icon: '🎤' },
  ama: { label: 'AMA', tone: 'butter', icon: '💬' },
  contest: { label: 'Contest', tone: 'violet', icon: '🏁' },
  info_session: { label: 'Info Session', tone: 'blue', icon: 'ℹ️' },
  diversity: { label: 'Diversity Programme', tone: 'rose', icon: '🌷' },
  ideathon: { label: 'Ideathon', tone: 'butter', icon: '💡' },
  certification: { label: 'Certification', tone: 'mint', icon: '🎓' },
  mock_interview: { label: 'Mock Interview', tone: 'peach', icon: '🗣️' },
  conference: { label: 'Conference', tone: 'violet', icon: '🎪' },
  internship_drive: { label: 'Internship Drive', tone: 'mint', icon: '📋' },
};

export const typeMeta = (type: EventType) =>
  EVENT_TYPE_META[type] || { label: type, tone: 'blue', icon: '📅' };

/** "Sat, 12 Oct · 06:30 pm" */
export const formatEventDate = (iso: string): string => {
  if (!iso) return '';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  const day = d.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short' });
  let h = d.getHours();
  const m = String(d.getMinutes()).padStart(2, '0');
  const suffix = h >= 12 ? 'pm' : 'am';
  h = h % 12 || 12;
  return `${day} · ${String(h).padStart(2, '0')}:${m} ${suffix}`;
};

export const formatDuration = (minutes: number | null): string => {
  if (!minutes) return '';
  if (minutes < 60) return `${minutes} min`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  if (h >= 24) {
    const days = Math.round(h / 24);
    return `${days} day${days > 1 ? 's' : ''}`;
  }
  return m ? `${h}h ${m}m` : `${h}h`;
};

export const formatPrice = (price: number, currency: string): string =>
  !price ? 'Free' : `${currency === 'INR' ? '₹' : ''}${price.toLocaleString('en-IN')}`;

/** Days until the event, as a short relative label. */
export const countdownLabel = (iso: string): string => {
  if (!iso) return '';
  const diff = new Date(iso).getTime() - Date.now();
  if (diff < 0) return 'Ended';
  const days = Math.floor(diff / 86400000);
  if (days === 0) return 'Today';
  if (days === 1) return 'Tomorrow';
  if (days < 7) return `In ${days} days`;
  const weeks = Math.floor(days / 7);
  return `In ${weeks} week${weeks > 1 ? 's' : ''}`;
};
