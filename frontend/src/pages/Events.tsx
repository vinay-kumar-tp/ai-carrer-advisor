import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { CalendarDays, Filter, Search, Sparkles, Ticket, X } from 'lucide-react';
import api from '../services/api';
import '../styles/events.css';
import { ToastHost, useToasts } from '../components/profile/ui';
import { errorMessage } from './profile/useProfileData';
import { EventCardItem } from './events/EventCardItem';
import { EventDetailDrawer } from './events/EventDetailDrawer';
import { RegisterModal } from './events/RegisterModal';
import type { EventCard, EventDetail, EventFacets, EventFilters, EventListResponse } from './events/types';
import { EMPTY_FILTERS, EVENT_TYPE_META, typeMeta } from './events/types';

const TABS = [
  { key: 'upcoming', label: 'Upcoming' },
  { key: 'registered', label: 'My Registrations' },
  { key: 'past', label: 'Past' },
  { key: '', label: 'All' },
];

const MODES = ['Online', 'In Person', 'Hybrid'];

export const EventsPage: React.FC = () => {
  const { toasts, push, dismiss } = useToasts();

  const [events, setEvents] = useState<EventCard[]>([]);
  const [total, setTotal] = useState(0);
  const [facets, setFacets] = useState<EventFacets | null>(null);
  const [filters, setFilters] = useState<EventFilters>(EMPTY_FILTERS);
  const [tab, setTab] = useState('upcoming');
  const [loading, setLoading] = useState(true);
  const [showFilters, setShowFilters] = useState(false);

  const [detail, setDetail] = useState<EventDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [showRegister, setShowRegister] = useState(false);

  const params = useMemo(() => {
    const p: Record<string, any> = { limit: 60, sort: filters.sort };
    if (tab) p.status = tab;
    if (filters.keyword) p.keyword = filters.keyword;
    if (filters.event_type) p.event_type = filters.event_type;
    if (filters.mode) p.mode = filters.mode;
    if (filters.host) p.host = filters.host;
    if (filters.city) p.city = filters.city;
    if (filters.price) p.price = filters.price;
    return p;
  }, [filters, tab]);

  const fetchEvents = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get<EventListResponse>('/events/', { params });
      setEvents(res.data.items);
      setTotal(res.data.total);
    } catch (error) {
      push(errorMessage(error, 'Could not load events.'), 'error');
    } finally {
      setLoading(false);
    }
  }, [params, push]);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  useEffect(() => {
    api
      .get<EventFacets>('/events/facets')
      .then((r) => setFacets(r.data))
      .catch(() => {});
  }, []);

  const patch = (p: Partial<EventFilters>) => setFilters((f) => ({ ...f, ...p }));
  const clearFilters = () => setFilters((f) => ({ ...EMPTY_FILTERS, keyword: f.keyword, sort: f.sort }));

  const activeFilterCount = [
    filters.event_type,
    filters.mode,
    filters.host,
    filters.city,
    filters.price,
  ].filter(Boolean).length;

  const openEvent = async (id: string) => {
    setDrawerOpen(true);
    setDetail(null);
    setDetailLoading(true);
    try {
      const res = await api.get<EventDetail>(`/events/${id}`);
      setDetail(res.data);
    } catch (error) {
      push(errorMessage(error, 'Could not load that event.'), 'error');
      setDrawerOpen(false);
    } finally {
      setDetailLoading(false);
    }
  };

  const closeDrawer = () => {
    setDrawerOpen(false);
    setDetail(null);
    setShowRegister(false);
  };

  const submitRegistration = async (payload: Record<string, any>) => {
    if (!detail) return;
    const res = await api.post(`/events/${detail.id}/register`, payload);
    push(res.data.message || 'Registration confirmed');
    setShowRegister(false);
    const fresh = await api.get<EventDetail>(`/events/${detail.id}`);
    setDetail(fresh.data);
    fetchEvents();
  };

  const cancelRegistration = async () => {
    if (!detail) return;
    try {
      await api.delete(`/events/${detail.id}/register`);
      push('Registration cancelled');
      const fresh = await api.get<EventDetail>(`/events/${detail.id}`);
      setDetail(fresh.data);
      fetchEvents();
    } catch (error) {
      push(errorMessage(error, 'Could not cancel your registration.'), 'error');
    }
  };

  const featured = events.filter((e) => e.is_featured && !e.is_past).slice(0, 1)[0];

  return (
    <div className="ev">
      <header className="ev-hero">
        <div className="ev-hero-text">
          <span className="ev-hero-kicker">
            <Sparkles size={12} /> Curated for your career
          </span>
          <h1>Events &amp; Opportunities</h1>
          <p>
            Hackathons, workshops, career fairs and certification drives hosted by leading technology
            companies. Register in a couple of taps — we pre-fill what we already know about you.
          </p>
        </div>
        {facets && (
          <div className="ev-hero-stats">
            <div className="ev-stat">
              <b>{facets.total}</b>
              <span>Live events</span>
            </div>
            <div className="ev-stat">
              <b>{facets.hosts.length}</b>
              <span>Host companies</span>
            </div>
            <div className="ev-stat">
              <b>{facets.event_types.length}</b>
              <span>Formats</span>
            </div>
          </div>
        )}
      </header>

      <nav className="ev-tabs" role="tablist" aria-label="Event views">
        {TABS.map((t) => (
          <button
            key={t.key || 'all'}
            role="tab"
            aria-selected={tab === t.key}
            className={`ev-tab${tab === t.key ? ' is-active' : ''}`}
            onClick={() => setTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </nav>

      <div className="ev-toolbar">
        <div className="ev-search">
          <Search size={15} />
          <input
            className="ev-input"
            placeholder="Search events, hosts or topics..."
            value={filters.keyword}
            onChange={(e) => patch({ keyword: e.target.value })}
            aria-label="Search events"
          />
          {filters.keyword && (
            <button className="ev-search-clear" onClick={() => patch({ keyword: '' })} aria-label="Clear search">
              <X size={13} />
            </button>
          )}
        </div>

        <button
          className={`ev-btn ev-btn-outline${showFilters ? ' is-active' : ''}`}
          onClick={() => setShowFilters((v) => !v)}
          aria-expanded={showFilters}
        >
          <Filter size={14} /> Filters
          {activeFilterCount > 0 && <span className="ev-filter-count">{activeFilterCount}</span>}
        </button>

        <select
          className="ev-input ev-sort"
          value={filters.sort}
          onChange={(e) => patch({ sort: e.target.value })}
          aria-label="Sort events"
        >
          <option value="soonest">Soonest first</option>
          <option value="newest">Recently added</option>
          <option value="seats">Most popular</option>
        </select>
      </div>

      {showFilters && (
        <div className="ev-filters cp-fade-up">
          <div className="ev-filter-group">
            <label>Format</label>
            <div className="ev-chip-row">
              {(Object.keys(EVENT_TYPE_META) as (keyof typeof EVENT_TYPE_META)[]).map((key) => (
                <button
                  key={key}
                  className={`ev-choice${filters.event_type === key ? ' is-active' : ''}`}
                  onClick={() => patch({ event_type: filters.event_type === key ? '' : key })}
                >
                  {typeMeta(key).icon} {typeMeta(key).label}
                </button>
              ))}
            </div>
          </div>

          <div className="ev-filter-row">
            <div className="ev-filter-group">
              <label>Mode</label>
              <div className="ev-chip-row">
                {MODES.map((m) => (
                  <button
                    key={m}
                    className={`ev-choice${filters.mode === m ? ' is-active' : ''}`}
                    onClick={() => patch({ mode: filters.mode === m ? '' : m })}
                  >
                    {m}
                  </button>
                ))}
              </div>
            </div>

            <div className="ev-filter-group">
              <label>Price</label>
              <div className="ev-chip-row">
                {[
                  { k: 'free', l: 'Free' },
                  { k: 'paid', l: 'Paid' },
                ].map((o) => (
                  <button
                    key={o.k}
                    className={`ev-choice${filters.price === o.k ? ' is-active' : ''}`}
                    onClick={() => patch({ price: filters.price === o.k ? '' : o.k })}
                  >
                    {o.l}
                  </button>
                ))}
              </div>
            </div>

            <div className="ev-filter-group">
              <label htmlFor="ev-host-filter">Host</label>
              <select
                id="ev-host-filter"
                className="ev-input"
                value={filters.host}
                onChange={(e) => patch({ host: e.target.value })}
              >
                <option value="">All hosts</option>
                {(facets?.hosts || []).map((h) => (
                  <option key={h.name} value={h.name}>
                    {h.name} ({h.count})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {activeFilterCount > 0 && (
            <button className="ev-btn ev-btn-ghost ev-clear" onClick={clearFilters}>
              Clear all filters
            </button>
          )}
        </div>
      )}

      {featured && tab === 'upcoming' && !filters.keyword && activeFilterCount === 0 && (
        <button className="ev-spotlight cp-fade-up" onClick={() => openEvent(featured.id)}>
          <div className="ev-spotlight-badge">
            <Sparkles size={12} /> Spotlight
          </div>
          <h2>{featured.title}</h2>
          <p>{featured.description}</p>
          <span className="ev-spotlight-cta">
            <Ticket size={14} /> View details and register
          </span>
        </button>
      )}

      <div className="ev-result-meta">
        <span>
          {loading ? 'Loading...' : `${total} event${total === 1 ? '' : 's'}`}
          {tab === 'registered' && !loading && total === 0 && ' — nothing yet'}
        </span>
      </div>

      {loading ? (
        <div className="ev-grid">
          {Array.from({ length: 6 }).map((_, i) => (
            <div className="ev-skeleton" key={i} />
          ))}
        </div>
      ) : events.length === 0 ? (
        <div className="ev-empty">
          <CalendarDays size={26} />
          <b>No events match this view</b>
          <span>
            {tab === 'registered'
              ? 'Register for an event and it will show up here with your ticket.'
              : 'Try clearing a filter or switching tabs.'}
          </span>
        </div>
      ) : (
        <div className="ev-grid cp-stagger">
          {events.map((e) => (
            <EventCardItem key={e.id} event={e} onOpen={openEvent} />
          ))}
        </div>
      )}

      {drawerOpen && (
        <EventDetailDrawer
          event={detail}
          loading={detailLoading}
          onClose={closeDrawer}
          onRegister={() => setShowRegister(true)}
          onCancel={cancelRegistration}
        />
      )}

      {showRegister && detail && (
        <RegisterModal event={detail} onClose={() => setShowRegister(false)} onSubmit={submitRegistration} />
      )}

      <ToastHost toasts={toasts} onDismiss={dismiss} />
    </div>
  );
};

export default EventsPage;
