import React, { useEffect, useMemo, useState } from 'react';
import { Search, Play, ChevronDown } from 'lucide-react';
import api from '../../services/api';
import { Loading, EmptyState } from '../../components/codequest/ui';
import { PracticeRunner } from './PracticeRunner';
import type { Catalog, TopicCard, SectionKey } from './types';
import { SECTION_ORDER, SECTION_TINT } from './types';

interface Props {
  notify: (msg: string, tone?: 'success' | 'error') => void;
  activeTopic: string | null;
  onOpenTopic: (slug: string | null) => void;
}

const SECTION_CHIP_CLASS: Record<SectionKey, string> = {
  quant: 'q', logical: 'l', verbal: 'v', technical: 't',
};

export const PracticeTab: React.FC<Props> = ({ notify, activeTopic, onOpenTopic }) => {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [section, setSection] = useState<SectionKey | 'all'>('all');
  const [query, setQuery] = useState('');
  const [expanded, setExpanded] = useState<string | null>(null);   // topic slug whose subtopics are open
  const [runner, setRunner] = useState<{ slug: string; name: string; subtopic?: string } | null>(null);

  const loadCatalog = () => {
    api
      .get<Catalog>('/aptitude/catalog')
      .then(({ data }) => setCatalog(data))
      .catch(() => setCatalog(null));
  };

  useEffect(() => { loadCatalog(); }, []);

  // Restore runner from URL (?topic=slug)
  useEffect(() => {
    if (activeTopic && catalog && !runner) {
      const topic = catalog.sections.flatMap((s) => s.topics).find((t) => t.slug === activeTopic);
      if (topic) setRunner({ slug: topic.slug, name: topic.name });
    }
    if (!activeTopic && runner) setRunner(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTopic, catalog]);

  const allTopics = useMemo(
    () => (catalog ? catalog.sections.flatMap((s) => s.topics) : []),
    [catalog],
  );

  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return allTopics.filter((t) => {
      if (section !== 'all' && t.section !== section) return false;
      if (needle && !t.name.toLowerCase().includes(needle) &&
          !t.subtopics.some((s) => s.name.toLowerCase().includes(needle))) return false;
      return true;
    });
  }, [allTopics, section, query]);

  const startPractice = (topic: TopicCard, subtopic?: string) => {
    setRunner({ slug: topic.slug, name: topic.name, subtopic });
    onOpenTopic(topic.slug);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const closeRunner = () => {
    setRunner(null);
    onOpenTopic(null);
    loadCatalog(); // refresh solved counts
  };

  if (runner) {
    return (
      <PracticeRunner
        topicSlug={runner.slug}
        topicName={runner.name}
        subtopic={runner.subtopic}
        onBack={closeRunner}
        notify={notify}
        onProgressChanged={() => { /* counts refresh on close */ }}
      />
    );
  }

  if (!catalog) return <Loading label="Loading catalog…" />;

  // group filtered topics by section for section headers when "all"
  const grouped = SECTION_ORDER
    .map((key) => ({
      key,
      label: catalog.section_labels[key] || key,
      topics: filtered.filter((t) => t.section === key),
    }))
    .filter((g) => g.topics.length > 0);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <div className="aq-search">
          <Search size={15} color="var(--text-muted)" />
          <input
            placeholder='Search topics — "percentage", "syllogism", "python"…'
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
      </div>

      <div className="aq-filter-row">
        <button className={`aq-chip all ${section === 'all' ? 'is-active' : ''}`} onClick={() => setSection('all')}>
          All sections
        </button>
        {SECTION_ORDER.map((key) => (
          <button
            key={key}
            className={`aq-chip ${SECTION_CHIP_CLASS[key]} ${section === key ? 'is-active' : ''}`}
            onClick={() => setSection(key)}
          >
            {catalog.section_labels[key]?.replace(' Aptitude', '').replace(' Reasoning', '').replace(' Ability', '').replace(' MCQs', '') || key}
          </button>
        ))}
        <span style={{ marginLeft: 'auto', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          {catalog.total_topics} topics · {catalog.total_questions} questions
        </span>
      </div>

      {grouped.length === 0 ? (
        <EmptyState title="No topics match" text="Try a different search or section." />
      ) : (
        grouped.map((g) => (
          <div key={g.key}>
            {section === 'all' && (
              <div className="aq-section-title">
                <span className="aq-section-dot" style={{ background: SECTION_TINT[g.key] }} />
                {g.label}
              </div>
            )}
            <div className="aq-grid">
              {g.topics.map((topic) => {
                const pct = topic.question_count ? Math.round((topic.solved_count / topic.question_count) * 100) : 0;
                const isOpen = expanded === topic.slug;
                return (
                  <div key={topic.slug} className="aq-card" style={{ ['--tint' as any]: SECTION_TINT[topic.section] }}>
                    <div className="aq-card-head">
                      <span className="aq-card-icon">{topic.icon || '📘'}</span>
                      <div style={{ flex: 1 }}>
                        <h3>{topic.name}</h3>
                        <div className="aq-card-meta">
                          {topic.subtopics.length} sub-topics · {topic.question_count} questions
                        </div>
                      </div>
                    </div>

                    <div className="aq-card-meta">
                      {topic.solved_count > 0 ? `${topic.solved_count}/${topic.question_count} solved` : 'Not practised yet'}
                    </div>
                    <div className="aq-progress-line">
                      <div className="aq-progress-fill" style={{ width: `${pct}%` }} />
                    </div>

                    <div className="aq-card-actions">
                      <button className="aq-btn" onClick={() => startPractice(topic)}>
                        <Play size={13} /> Practise
                      </button>
                      <button className="aq-link" onClick={() => setExpanded(isOpen ? null : topic.slug)}>
                        Pick a subtopic <ChevronDown size={13} style={{ transform: isOpen ? 'rotate(180deg)' : 'none' }} />
                      </button>
                    </div>

                    {isOpen && (
                      <div className="aq-subs">
                        {topic.subtopics.map((sub) => (
                          <div key={sub.name} className="aq-sub-row" onClick={() => startPractice(topic, sub.name)}>
                            <span>{sub.name}</span>
                            <span className="aq-sub-count">{sub.question_count} Q</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))
      )}
    </div>
  );
};
