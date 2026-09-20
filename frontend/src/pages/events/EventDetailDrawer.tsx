import React from 'react';
import {
  Award,
  CalendarDays,
  CheckCircle2,
  Clock,
  Gift,
  ListChecks,
  MapPin,
  Mic2,
  Ticket,
  Trophy,
  Users,
  X,
} from 'lucide-react';
import { HostLogo } from './HostLogo';
import type { EventDetail } from './types';
import { formatDuration, formatEventDate, formatPrice, typeMeta } from './types';

type Props = {
  event: EventDetail | null;
  loading: boolean;
  onClose: () => void;
  onRegister: () => void;
  onCancel: () => void;
};

export const EventDetailDrawer: React.FC<Props> = ({ event, loading, onClose, onRegister, onCancel }) => (
  <div className="ev-drawer-overlay" onClick={onClose} role="presentation">
    <aside
      className="ev-drawer"
      onClick={(e) => e.stopPropagation()}
      role="dialog"
      aria-modal="true"
      aria-label={event?.title || 'Event details'}
    >
      <button className="ev-drawer-close" onClick={onClose} aria-label="Close">
        <X size={16} />
      </button>

      {loading && <div className="ev-drawer-loading">Loading event...</div>}

      {event && !loading && (
        <>
          <div className="ev-drawer-head">
            <HostLogo
              company={event.host_company}
              domain={event.host_domain}
              fallback={event.host_logo}
              className="ev-logo is-lg"
            />
            <div>
              <span className={`ev-type-pill tone-${typeMeta(event.event_type).tone}`}>
                <span aria-hidden="true">{typeMeta(event.event_type).icon}</span>{' '}
                {typeMeta(event.event_type).label}
              </span>
              <h2>{event.title}</h2>
              <div className="ev-drawer-sub">
                {event.host_company}
                {event.host_tagline ? ` · ${event.host_tagline}` : ''}
              </div>
            </div>
          </div>

          <div className="ev-fact-grid">
            <div className="ev-fact">
              <CalendarDays size={14} />
              <div>
                <span>When</span>
                <b>
                  {formatEventDate(event.event_date)} {event.timezone_label}
                </b>
              </div>
            </div>
            <div className="ev-fact">
              <Clock size={14} />
              <div>
                <span>Duration</span>
                <b>{formatDuration(event.duration_minutes) || 'See agenda'}</b>
              </div>
            </div>
            <div className="ev-fact">
              <MapPin size={14} />
              <div>
                <span>{event.mode}</span>
                <b>{event.venue || event.location || 'Online'}</b>
              </div>
            </div>
            <div className="ev-fact">
              <Users size={14} />
              <div>
                <span>Seats</span>
                <b>
                  {event.capacity
                    ? `${event.seats_left} left of ${event.capacity}`
                    : 'Unlimited'}
                </b>
              </div>
            </div>
            <div className="ev-fact">
              <Ticket size={14} />
              <div>
                <span>Fee</span>
                <b>{formatPrice(event.price, event.currency)}</b>
              </div>
            </div>
            {event.is_certified && (
              <div className="ev-fact">
                <Award size={14} />
                <div>
                  <span>Certificate</span>
                  <b>Issued on completion</b>
                </div>
              </div>
            )}
          </div>

          {event.about && (
            <section className="ev-section">
              <h4>About this event</h4>
              {event.about.split('\n\n').map((para, i) => (
                <p key={i}>{para}</p>
              ))}
            </section>
          )}

          {event.agenda.length > 0 && (
            <section className="ev-section">
              <h4>
                <ListChecks size={15} /> Agenda
              </h4>
              <ol className="ev-agenda">
                {event.agenda.map((item, i) => (
                  <li key={i}>
                    <span className="ev-agenda-time">{item.time}</span>
                    <div>
                      <b>{item.title}</b>
                      {item.detail && <p>{item.detail}</p>}
                    </div>
                  </li>
                ))}
              </ol>
            </section>
          )}

          {event.speakers.length > 0 && (
            <section className="ev-section">
              <h4>
                <Mic2 size={15} /> Speakers
              </h4>
              <div className="ev-speakers">
                {event.speakers.map((s, i) => (
                  <div className="ev-speaker" key={i}>
                    <div className="ev-speaker-avatar" aria-hidden="true">
                      {s.name.charAt(0)}
                    </div>
                    <div>
                      <b>{s.name}</b>
                      <span>
                        {s.title}
                        {s.company ? ` · ${s.company}` : ''}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {event.prizes.length > 0 && (
            <section className="ev-section">
              <h4>
                <Trophy size={15} /> Prizes
              </h4>
              <ul>
                {event.prizes.map((x, i) => (
                  <li key={i}>{x}</li>
                ))}
              </ul>
            </section>
          )}

          {event.perks.length > 0 && (
            <section className="ev-section">
              <h4>
                <Gift size={15} /> What you get
              </h4>
              <div className="ev-chip-row">
                {event.perks.map((x) => (
                  <span className="ev-tag" key={x}>
                    {x}
                  </span>
                ))}
              </div>
            </section>
          )}

          {event.eligibility.length > 0 && (
            <section className="ev-section">
              <h4>
                <CheckCircle2 size={15} /> Who can attend
              </h4>
              <ul>
                {event.eligibility.map((x, i) => (
                  <li key={i}>{x}</li>
                ))}
              </ul>
            </section>
          )}

          <div className="ev-drawer-foot">
            {event.registered ? (
              <>
                <span className="ev-reg-flag is-lg">
                  <CheckCircle2 size={15} />
                  {event.registration_status === 'waitlisted' ? 'On the waitlist' : 'You are registered'}
                </span>
                <button className="ev-btn ev-btn-ghost" onClick={onCancel}>
                  Cancel registration
                </button>
              </>
            ) : event.is_past ? (
              <span className="ev-muted">This event has already taken place.</span>
            ) : (
              <button className="ev-btn ev-btn-primary" onClick={onRegister}>
                <Ticket size={15} /> {event.is_full ? 'Join the waitlist' : 'Register now'}
              </button>
            )}
          </div>
        </>
      )}
    </aside>
  </div>
);
