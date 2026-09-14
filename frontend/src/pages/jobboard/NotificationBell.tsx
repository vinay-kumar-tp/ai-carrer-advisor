import React, { useEffect, useRef, useState } from 'react';
import { Bell } from 'lucide-react';
import api from '../../services/api';
import type { AppNotification } from './types';
import { timeAgo } from './types';

export const NotificationBell: React.FC<{ refreshKey?: number }> = ({ refreshKey }) => {
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState<AppNotification[]>([]);
  const ref = useRef<HTMLDivElement>(null);

  const load = async () => {
    try {
      const res = await api.get('/notifications/');
      setItems(res.data);
    } catch {
      /* silent */
    }
  };

  useEffect(() => {
    load();
  }, [refreshKey]);

  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', onDown);
    return () => document.removeEventListener('mousedown', onDown);
  }, [open]);

  const unread = items.filter((i) => !i.read).length;

  const toggle = async () => {
    const next = !open;
    setOpen(next);
    if (next) await load();
  };

  const markAllRead = async () => {
    try {
      await api.put('/notifications/read-all');
      setItems((prev) => prev.map((i) => ({ ...i, read: true })));
    } catch {
      /* silent */
    }
  };

  return (
    <div className="jb-bell" ref={ref}>
      <button className="jb-bell-btn" onClick={toggle} aria-label="Notifications">
        <Bell size={18} />
        {unread > 0 && <span className="jb-bell-count">{unread > 9 ? '9+' : unread}</span>}
      </button>
      {open && (
        <div className="jb-notif-panel">
          <div className="jb-notif-head">
            <b>Notifications</b>
            {unread > 0 && (
              <button className="jb-notif-clear" onClick={markAllRead}>
                Mark all read
              </button>
            )}
          </div>
          {items.length === 0 ? (
            <div className="jb-notif-empty">No notifications yet.</div>
          ) : (
            items.map((n) => (
              <div key={n.id} className={`jb-notif-item${n.read ? '' : ' unread'}`}>
                {!n.read && <span className="dot" />}
                <div style={{ flex: 1 }}>
                  <div>{n.message}</div>
                  <div className="time">{timeAgo(n.created_at)}</div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};
