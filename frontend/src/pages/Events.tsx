import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { Calendar, MapPin, ExternalLink, CheckCircle2 } from 'lucide-react';

export const EventsPage: React.FC = () => {
  const [events, setEvents] = useState<any[]>([]);
  const [registeredEvents, setRegisteredEvents] = useState<string[]>([]);

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      const res = await api.get('/events/');
      setEvents(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRegister = async (eventId: string) => {
    try {
      await api.post(`/events/${eventId}/register`);
      setRegisteredEvents([...registeredEvents, eventId]);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Registration failed');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <h2>Career Events, Fairs & Webinars</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Join live workshops, virtual career expos, and expert Q&A panels with recruiters.</p>
      </div>

      <div className="grid-2">
        {events.map((e) => {
          const isReg = registeredEvents.includes(e.id);
          return (
            <div key={e.id} className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                  <span className="badge badge-indigo">Upcoming Event</span>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Capacity: {e.capacity || 'Unlimited'}</span>
                </div>
                <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>{e.title}</h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '1rem' }}>{e.description}</p>
                <div style={{ display: 'flex', gap: '1rem', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}><Calendar size={14} /> {new Date(e.event_date).toLocaleDateString()}</span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}><MapPin size={14} /> {e.location}</span>
                </div>
              </div>

              <div>
                {isReg ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#34d399', fontWeight: 600 }}>
                    <CheckCircle2 size={18} /> Registered for Webinar
                  </div>
                ) : (
                  <button onClick={() => handleRegister(e.id)} className="btn btn-primary" style={{ width: '100%' }}>
                    RSVP & Register
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
