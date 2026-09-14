import React from 'react';
import { SlidersHorizontal } from 'lucide-react';
import type { Facets, Filters } from './types';

const EXPERIENCE_BANDS = [
  { label: '0-1 yr', min: '0', max: '1' },
  { label: '1-3 yr', min: '1', max: '3' },
  { label: '3-5 yr', min: '3', max: '5' },
  { label: '5-8 yr', min: '5', max: '8' },
  { label: '8+ yr', min: '8', max: '' },
];

const CTC_BANDS = [
  { label: '0-3 LPA', min: '0', max: '300000' },
  { label: '3-6 LPA', min: '300000', max: '600000' },
  { label: '6-10 LPA', min: '600000', max: '1000000' },
  { label: '10-20 LPA', min: '1000000', max: '2000000' },
  { label: '20-40 LPA', min: '2000000', max: '4000000' },
  { label: '40 LPA+', min: '4000000', max: '' },
];

const STIPEND_BANDS = [
  { label: '0-10K', min: '0', max: '10000' },
  { label: '10-25K', min: '10000', max: '25000' },
  { label: '25-50K', min: '25000', max: '50000' },
  { label: '50K+', min: '50000', max: '' },
];

const POSTED_BANDS = [
  { label: 'Last 7 days', value: '7' },
  { label: 'Last 30 days', value: '30' },
  { label: 'Last 60 days', value: '60' },
];

type Props = {
  facets: Facets | null;
  filters: Filters;
  onChange: (patch: Partial<Filters>) => void;
  onClear: () => void;
};

export const FilterSidebar: React.FC<Props> = ({ facets, filters, onChange, onClear }) => {
  const select = (
    key: keyof Filters,
    label: string,
    options: { name: string; count?: number }[],
    allLabel: string,
  ) => (
    <div className="jb-fgroup">
      <label>{label}</label>
      <select
        className="jb-select"
        value={filters[key]}
        onChange={(e) => onChange({ [key]: e.target.value } as Partial<Filters>)}
      >
        <option value="">{allLabel}</option>
        {options.map((o) => (
          <option key={o.name} value={o.name}>
            {o.name}
            {o.count != null ? ` (${o.count})` : ''}
          </option>
        ))}
      </select>
    </div>
  );

  const bandChips = (
    key: 'experience' | 'ctc' | 'stipend' | 'posted',
    bands: any[],
  ) => (
    <div className="jb-chips">
      {bands.map((b) => {
        let active = false;
        if (key === 'posted') active = filters.posted_in === b.value;
        else if (key === 'experience') active = filters.min_experience === b.min && filters.max_experience === b.max;
        else if (key === 'ctc') active = filters.min_ctc === b.min && filters.max_ctc === b.max;
        else active = filters.min_stipend === b.min && filters.max_stipend === b.max;

        const toggle = () => {
          if (key === 'posted') onChange({ posted_in: active ? '' : b.value });
          else if (key === 'experience') onChange(active ? { min_experience: '', max_experience: '' } : { min_experience: b.min, max_experience: b.max });
          else if (key === 'ctc') onChange(active ? { min_ctc: '', max_ctc: '' } : { min_ctc: b.min, max_ctc: b.max });
          else onChange(active ? { min_stipend: '', max_stipend: '' } : { min_stipend: b.min, max_stipend: b.max });
        };

        return (
          <button key={b.label} className={`jb-chip${active ? ' active' : ''}`} onClick={toggle} type="button">
            {b.label}
          </button>
        );
      })}
    </div>
  );

  const jobTypes = facets?.job_types.map((f) => ({ name: f.name, count: f.count })) ?? [];

  return (
    <div className="glass-card jb-sidebar">
      <div className="jb-filter-head">
        <b>
          <SlidersHorizontal size={15} style={{ verticalAlign: -3, marginRight: 6 }} />
          Filters
        </b>
        <button className="jb-clear" onClick={onClear} type="button">
          Clear all
        </button>
      </div>

      {select('job_type', 'Job Type', jobTypes, 'All types')}
      <div className="jb-fgroup">
        <label>Job Status</label>
        <div className="jb-chips">
          {[
            { l: 'Applied', v: 'applied' },
            { l: 'Not applied', v: 'not_applied' },
          ].map((s) => (
            <button
              key={s.v}
              type="button"
              className={`jb-chip${filters.status === s.v ? ' active' : ''}`}
              onClick={() => onChange({ status: filters.status === s.v ? '' : s.v })}
            >
              {s.l}
            </button>
          ))}
        </div>
      </div>

      {select('role', 'Job Role', facets?.roles ?? [], 'All roles')}
      {select('location', 'Location', facets?.locations ?? [], 'All locations')}
      {select('industry', 'Industry', facets?.industries ?? [], 'All industries')}
      {select('employer', 'Employer', facets?.employers ?? [], 'All employers')}
      {select('source_portal', 'Source Portal', facets?.portals ?? [], 'All portals')}

      <div className="jb-fgroup">
        <label>Onsite / Remote</label>
        <div className="jb-chips">
          {['In Office', 'Remote', 'Hybrid'].map((m) => (
            <button
              key={m}
              type="button"
              className={`jb-chip${filters.employment_mode === m ? ' active' : ''}`}
              onClick={() => onChange({ employment_mode: filters.employment_mode === m ? '' : m })}
            >
              {m}
            </button>
          ))}
        </div>
      </div>

      <div className="jb-fgroup">
        <label>Years of Experience</label>
        {bandChips('experience', EXPERIENCE_BANDS)}
      </div>

      <div className="jb-fgroup">
        <label>Job Posted In</label>
        {bandChips('posted', POSTED_BANDS)}
      </div>

      <div className="jb-fgroup">
        <label>CTC (Annual)</label>
        {bandChips('ctc', CTC_BANDS)}
      </div>

      <div className="jb-fgroup">
        <label>Stipend (Monthly)</label>
        {bandChips('stipend', STIPEND_BANDS)}
      </div>
    </div>
  );
};
