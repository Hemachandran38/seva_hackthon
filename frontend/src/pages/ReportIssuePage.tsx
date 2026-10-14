import { cloneElement, useEffect, useState, type ChangeEvent, type FormEvent, type ReactElement, type ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle, Check, ShieldCheck, UploadCloud, X } from 'lucide-react';
import { complaintService } from '../services/complaintService';
import { LocationSelector } from '../components/map/LocationSelector';
import type { NewComplaint } from '../types/complaint';
import { PageIntro } from '../components/common/Ui';

type Fields = { 
  category: string; 
  fault: string; 
  title: string; 
  description: string; 
  location: string; 
  ward: string; 
  assetId: string; 
  latitude?: number; 
  longitude?: number 
};

const initial: Fields = {
  category: 'Streetlight',
  fault: 'Not working / blackout',
  title: '',
  description: '',
  location: '',
  ward: 'Ward 12',
  assetId: '',
};

export function ReportIssuePage() {
  const [fields, setFields] = useState(initial);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState('');
  const [errors, setErrors] = useState<Partial<Record<keyof Fields | 'photo', string>>>({});
  const [saved, setSaved] = useState('');
  const [saveError, setSaveError] = useState('');

  useEffect(() => {
    if (!file) {
      setPreview('');
      return;
    }
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const update = (key: keyof Fields, value: string | number | undefined) => {
    setFields((old) => ({ ...old, [key]: value }));
    setErrors((old) => ({ ...old, [key]: '' }));
    setSaveError('');
  };

  const chooseFile = (event: ChangeEvent<HTMLInputElement>) => {
    const selected = event.target.files?.[0];
    if (!selected) return;
    if (!selected.type.startsWith('image/')) {
      setErrors((old) => ({ ...old, photo: 'Choose a JPEG, PNG, WebP or other image file.' }));
      event.target.value = '';
      return;
    }
    if (selected.size > 5 * 1024 * 1024) {
      setErrors((old) => ({ ...old, photo: 'Image must be 5 MB or smaller.' }));
      event.target.value = '';
      return;
    }
    setErrors((old) => ({ ...old, photo: '' }));
    setFile(selected);
  };

  const submit = (event: FormEvent) => {
    event.preventDefault();
    const next: typeof errors = {};
    for (const key of ['title', 'description', 'location'] as const)
      if (!fields[key].trim()) next[key] = 'This field is required.';
    if (fields.title.trim().length < 5) next.title = 'Enter at least 5 characters.';
    if (fields.description.trim().length < 10) next.description = 'Please provide at least 10 characters.';
    setErrors(next);
    if (Object.values(next).some(Boolean)) return;

    const input: NewComplaint = {
      title: fields.title.trim(),
      description: `${fields.fault}. ${fields.description.trim()}`,
      location: fields.location.trim(),
      category: fields.category,
      ...(fields.ward && { ward: fields.ward }),
      ...(fields.assetId.trim() && { assetId: fields.assetId.trim() }),
      ...(fields.latitude !== undefined && fields.longitude !== undefined && {
        latitude: fields.latitude,
        longitude: fields.longitude,
      }),
    };
    const result = complaintService.createComplaint(input);
    if (!result.saved) {
      setSaveError('The complaint could not be saved to this browser. Check browser storage and try again.');
      return;
    }
    setSaved(result.complaint.id);
    setFields(initial);
    setFile(null);
    setErrors({});
  };

  if (saved)
    return (
      <>
        <PageIntro eyebrow="PUBLIC ASSET INGESTION" title="Report an Infrastructure Issue">
          Your report has been saved to this browser's local demonstration registry.
        </PageIntro>
        <section className="section-width success-panel">
          <span className="success-mark">
            <Check />
          </span>
          <div>
            <div className="section-kicker">REPORT RECEIVED</div>
            <h2>
              Your sample complaint ID is <span className="mono">{saved}</span>
            </h2>
            <p>Keep this reference number to track the report. This demonstration does not send information to a municipal service.</p>
            <div className="hero-actions">
              <Link className="button primary" to={`/track?id=${encodeURIComponent(saved)}`}>
                Track this complaint
              </Link>
              <Link className="button secondary" to="/issues">
                View issue registry
              </Link>
              <button className="text-link" onClick={() => setSaved('')}>
                Submit another report
              </button>
            </div>
          </div>
        </section>
      </>
    );

  return (
    <>
      <PageIntro eyebrow="PUBLIC ASSET INGESTION · LOCAL DEMO" title="Report an Infrastructure Issue">
        Submit an asset defect report. Sample submissions are saved in this browser and can be tracked in the demonstration registry.
      </PageIntro>
      <div className="report-layout section-width">
        <form className="report-form" onSubmit={submit} noValidate>
          <section className="form-section">
            <SectionTitle
              number="01"
              title="Issue Classification"
              hint="Identify the infrastructure category and failure profile."
              required
            />
            <div className="form-grid">
              <Field label="Infrastructure domain" required error={errors.category}>
                <select value={fields.category} onChange={(e) => update('category', e.target.value)}>
                  <option>Streetlight</option>
                  <option>Road & pavement</option>
                  <option>Drainage</option>
                  <option>Public space</option>
                  <option>Electrical Hazard</option>
                </select>
              </Field>
              <Field label="Observed fault characteristic">
                <select value={fields.fault} onChange={(e) => update('fault', e.target.value)}>
                  <option>Not working / blackout</option>
                  <option>Flickering or intermittent</option>
                  <option>Damaged / exposed wiring</option>
                  <option>Physical damage</option>
                  <option>Other fault</option>
                </select>
              </Field>
              <Field className="span-2" label="Summary title" required error={errors.title}>
                <input
                  value={fields.title}
                  onChange={(e) => update('title', e.target.value)}
                  maxLength={120}
                  placeholder="e.g. Streetlight out near the bus stop"
                />
              </Field>
              <Field className="span-2" label="Detailed incident description" required error={errors.description}>
                <textarea
                  value={fields.description}
                  onChange={(e) => update('description', e.target.value)}
                  maxLength={500}
                  rows={4}
                  placeholder="Describe what you observed and when."
                />
                <span className="field-help">{fields.description.length} / 500 characters</span>
              </Field>
            </div>
          </section>

          <section className="form-section">
            <SectionTitle
              number="02"
              title="Location & Asset Pinpointing"
              hint="Provide a location that a maintenance crew can find."
              required
            />
            <div className="form-grid">
              <Field label="Municipal ward">
                <select value={fields.ward} onChange={(e) => update('ward', e.target.value)}>
                  <option value="">Select ward (optional)</option>
                  <option>Ward 11</option>
                  <option>Ward 12</option>
                  <option>Ward 13</option>
                  <option>Other ward</option>
                </select>
              </Field>
              <Field label="Asset ID (if known)">
                <input
                  value={fields.assetId}
                  onChange={(e) => update('assetId', e.target.value)}
                  placeholder="e.g. SL-W12-004"
                />
              </Field>
              <Field className="span-2" label="Street address / landmark" required error={errors.location}>
                <input
                  value={fields.location}
                  onChange={(e) => update('location', e.target.value)}
                  placeholder="Street, neighbourhood, nearby landmark"
                />
              </Field>
            </div>
            <div className="form-grid">
              <Field className="span-2" label="Geographic Location (Optional)">
                <LocationSelector
                  latitude={fields.latitude}
                  longitude={fields.longitude}
                  onLocationSelect={(lat, lng) => {
                    update('latitude', lat);
                    update('longitude', lng);
                  }}
                  onLocationClear={() => {
                    update('latitude', undefined);
                    update('longitude', undefined);
                  }}
                />
              </Field>
            </div>
          </section>

          <section className="form-section">
            <SectionTitle number="03" title="Evidence & Media Verification" hint="A photograph can help explain the fault." />
            <label className="upload-box">
              {preview ? (
                <img src={preview} alt="Selected evidence preview" />
              ) : (
                <>
                  <UploadCloud size={25} />
                  <strong>Choose an infrastructure photo</strong>
                  <span>JPEG, PNG or WebP · Up to 5 MB</span>
                </>
              )}
              <input type="file" accept="image/*" onChange={chooseFile} />
            </label>
            {errors.photo && (
              <span className="field-error" role="alert">
                {errors.photo}
              </span>
            )}
            {file && (
              <div className="selected-file">
                <span>
                  {file.name} · {(file.size / 1024 / 1024).toFixed(2)} MB
                </span>
                <button type="button" aria-label="Remove selected photo" onClick={() => setFile(null)}>
                  <X size={16} />
                </button>
              </div>
            )}
            <p className="field-help">Photos are previewed for this session and are not stored with the local complaint record.</p>
          </section>

          <section className="form-section">
            <SectionTitle
              number="04"
              title="Citizen Contact & Dispatch Updates"
              hint="Optional contact details are not collected in this prototype."
            />
            <div className="privacy-note">
              <ShieldCheck size={18} />
              <p>
                <strong>Privacy note</strong>
                <br />
                This local demonstration stores the report in your browser only. Please do not include private personal information.
              </p>
            </div>
          </section>

          {saveError && (
            <div className="alert-error" role="alert">
              {saveError}
            </div>
          )}
          <div className="form-actions">
            <Link className="button secondary" to="/">
              Cancel and return home
            </Link>
            <button className="button primary" type="submit">
              <UploadCloud size={16} /> Submit Fault Report
            </button>
          </div>
        </form>

        <aside className="report-aside">
          <article className="aside-card">
            <h3>How Prioritization Works</h3>
            <p>Sample triage considers submitted details and service impact. This demo does not use a trained prediction model.</p>
            <div className="aside-info">
              <b>Transparent factors</b>
              <span>Severity · Repeat reports · Time pending · Public impact</span>
            </div>
            <div className="aside-info">
              <b>Local demonstration</b>
              <span>No report is routed to a real maintenance department.</span>
            </div>
          </article>
          <article className="aside-card hazard">
            <h3>
              <AlertTriangle size={16} /> Urgent hazard notice
            </h3>
            <p>For fallen live wires, structural collapse or another immediate danger, contact your local emergency service.</p>
          </article>
          <article className="aside-card ward-card">
            <span className="live-dot" /> Ward 12 Crew Status <b>Sample data only</b>
            <p>No live crew availability is connected.</p>
            <Link className="text-link" to="/issues">
              Browse sample reports →
            </Link>
          </article>
        </aside>
      </div>
    </>
  );
}

function SectionTitle({
  number,
  title,
  hint,
  required = false,
}: {
  number: string;
  title: string;
  hint: string;
  required?: boolean;
}) {
  return (
    <div className="form-title">
      <span>{number}</span>
      <div>
        <h2>{title}</h2>
        <p>{hint}</p>
      </div>
      {required && <small>REQUIRED FIELDS</small>}
    </div>
  );
}

function Field({
  label,
  required,
  error,
  className = '',
  children,
}: {
  label: string;
  required?: boolean;
  error?: string;
  className?: string;
  children: ReactNode;
}) {
  const id = label.toLowerCase().replaceAll(/[^a-z0-9]+/g, '-');
  return (
    <div className={`field ${className}`}>
      <label htmlFor={id}>
        {label}
        {required && <em> *</em>}
      </label>
      {children && cloneId(children, id, error)}
      {error && (
        <span id={`${id}-error`} className="field-error" role="alert">
          {error}
        </span>
      )}
    </div>
  );
}

function cloneId(children: ReactNode, id: string, error?: string) {
  if (typeof children === 'object' && children && 'type' in children) {
    const element = children as ReactElement<{ id?: string; 'aria-invalid'?: boolean; 'aria-describedby'?: string }>;
    return cloneElement(element, {
      id,
      'aria-invalid': Boolean(error),
      'aria-describedby': error ? `${id}-error` : undefined,
    });
  }
  return children;
}
