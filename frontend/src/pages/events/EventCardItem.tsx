import React from 'react';
import { Award, CalendarDays, CheckCircle2, Clock, MapPin, Sparkles, Users } from 'lucide-react';
import { HostLogo } from './HostLogo';
import type { EventCard } from './types';
import { countdownLabel, formatDuration, formatEventDate, formatPrice, typeMeta } from './types';

type Props = {
  event: EventCard;
  onOpen: (id: string) => void;
};

export const EventCardItem: React.FC<Props> = ({ event, onOpen }) => {
  const meta = typeMeta(event.event_type);
  const seatPct =
    event.capacity && event.capacity > 0
      ? Math.min(100, Math.round((event.seats_taken / event.capacity) * 100))
      : 0;

  return (
    <article
      className={`ev-card${event.is_past ? ' is-past' : ''}`}
      onClick={() => onOpen(event.id)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onOpen(event.id);
        }
      }}
      aria-label={`${event.title} — ${meta.label}`}
    >
      {event.is_featured && (
        <span className="ev-featured">
          <Sparkles size={11} /> Featured
        </span>
      )}

      <div className={`ev-card-band tone-${meta.tone}`} />

      <div className="ev-card-head">
        <HostLogo company={event.host_company} domain={event.host_domain} fallback={event.host_logo} />
        <div className="ev-card-head-text">
          <span className={`ev-type-pill tone-${meta.tone}`}>
            <span aria-hidden="true">{meta.icon}</span> {meta.label}
          </span>
          <div className="ev-host">{event.host_company}</div>
        </div>
        {event.registered && (
          <span className="ev-reg-flag" title={`Status: ${event.registration_status}`}>
            <CheckCircle2 size={14} />
            {event.registration_status === 'waitlisted' ? 'Waitlisted' : 'Registered'}
          </span>
        )}
      </div>

      <h3 className="ev-card-title">{event.title}</h3>
      <p className="ev-card-desc">{event.description}</p>

      <div className="ev-meta-grid">
        <span>
          <CalendarDays size={13} /> {formatEventDate(event.event_date)}
        </span>
        {event.duration_minutes && (
          <span>
            <Clock size={13} /> {formatDuration(event.duration_minutes)}
          </span>
        )}
        <span>
          <MapPin size={13} /> {event.mode === 'Online' ? 'Online' : event.city || event.location}
        </span>
        {event.capacity && (
          <span>
            <Users size={13} /> {event.seats_left ?? 0} seats left
          </span>
        )}
      </div>

      {event.capacity ? (
        <div className="ev-seat-bar" title={`${event.seats_taken} of ${event.capacity} seats taken`}>
          <div className={`ev-seat-fill${seatPct >= 90 ? ' is-tight' : ''}`} style={{ width: `${seatPct}%` }} />
        </div>
      ) : (
        <div className="ev-seat-spacer" />
      )}

      <div className="ev-card-foot">
        <div className="ev-tags">
          {event.tags.slice(0, 2).map((t) => (
            <span key={t} className="ev-tag">
              {t}
            </span>
          ))}
          {event.is_certified && (
            <span className="ev-tag is-cert">
              <Award size={11} /> Certificate
            </span>
          )}
        </div>
        <div className="ev-card-right">
          <span className={`ev-price${event.price ? '' : ' is-free'}`}>
            {formatPrice(event.price, event.currency)}
          </span>
          <span className="ev-countdown">{countdownLabel(event.event_date)}</span>
        </div>
      </div>
    </article>
  );
};
