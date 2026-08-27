import { useEffect, useMemo, useRef, useState } from "react";
import "./App.css";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const emptyForm = {
  project_name: "",
  wastewater_type: "",
  average_flow_m3_day: "",
  peak_flow_m3_day: "",
  influent_bod_mg_l: "",
  influent_cod_mg_l: "",
  influent_tss_mg_l: "",
  ammonia_mg_l: "",
  target_bod_mg_l: "",
  target_tss_mg_l: "",
  nitrification_required: false,
};

const templates = {
  municipal: {
    project_name: "Municipal WWTP — Example Basis",
    wastewater_type: "municipal",
    average_flow_m3_day: 10000,
    peak_flow_m3_day: 25000,
    influent_bod_mg_l: 250,
    influent_cod_mg_l: 500,
    influent_tss_mg_l: 300,
    ammonia_mg_l: 30,
    target_bod_mg_l: 20,
    target_tss_mg_l: 10,
    nitrification_required: true,
  },
  industrial: {
    project_name: "Industrial WWTP — Example Basis",
    wastewater_type: "industrial",
    average_flow_m3_day: 5000,
    peak_flow_m3_day: 12000,
    influent_bod_mg_l: 600,
    influent_cod_mg_l: 1200,
    influent_tss_mg_l: 450,
    ammonia_mg_l: 40,
    target_bod_mg_l: 30,
    target_tss_mg_l: 20,
    nitrification_required: true,
  },
};

function num(value, fallback = 0) {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

function fmt(value, digits = 2) {
  const n = Number(value);
  if (!Number.isFinite(n)) return "—";
  return n.toLocaleString("en-IN", {
    maximumFractionDigits: digits,
  });
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

const PROJECTS_KEY = "wwtp_design_projects_v2";

function loadSavedProjects() {
  try {
    const parsed = JSON.parse(localStorage.getItem(PROJECTS_KEY) || "[]");
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveSavedProjects(projects) {
  localStorage.setItem(PROJECTS_KEY, JSON.stringify(projects.slice(0, 12)));
}

function safeFileName(name) {
  return (name || "wwtp-design").replace(/[^a-z0-9]+/gi, "-").replace(/^-|-$/g, "").toLowerCase();
}

function downloadJson(data, filename) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function humanize(key) {
  return key
    .replaceAll("_", " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function flattenObject(obj, prefix = "") {
  const rows = [];

  if (!obj || typeof obj !== "object") return rows;

  Object.entries(obj).forEach(([key, value]) => {
    const label = prefix ? `${prefix} / ${humanize(key)}` : humanize(key);

    if (
      value &&
      typeof value === "object" &&
      !Array.isArray(value)
    ) {
      rows.push(...flattenObject(value, label));
    } else if (!Array.isArray(value)) {
      rows.push({ label, value });
    }
  });

  return rows;
}

function Metric({ label, value, unit }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
      {unit && <small>{unit}</small>}
    </div>
  );
}

function Section({ title, subtitle, children }) {
  return (
    <section className="result-section">
      <div className="section-heading">
        <div>
          <h2>{title}</h2>
          {subtitle && <p>{subtitle}</p>}
        </div>
      </div>
      {children}
    </section>
  );
}

function ArrayTable({ data, columns }) {
  if (!Array.isArray(data) || !data.length) {
    return <div className="empty">No data available.</div>;
  }

  const inferred = columns || Object.keys(data[0] || {}).map((key) => ({
    key,
    label: humanize(key),
  }));

  return (
    <div className="data-table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            {inferred.map((column) => <th key={column.key}>{column.label}</th>)}
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr key={row.equipment_id || row.name || index}>
              {inferred.map((column) => {
                const value = row?.[column.key];
                return (
                  <td key={column.key}>
                    {typeof value === "number" ? fmt(value) : value == null ? "—" : String(value)}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ProfileChart({ profile }) {
  const units = profile?.units || [];
  if (!units.length) return <div className="empty">No hydraulic profile available.</div>;
  const maxLoss = Math.max(...units.map((unit) => Number(unit.headloss_m) || 0), 0.1);

  return (
    <div className="profile-chart">
      {units.map((unit, index) => {
        const loss = Number(unit.headloss_m) || 0;
        return (
          <div className="profile-row" key={`${unit.name}-${index}`}>
            <div className="profile-index">{String(index + 1).padStart(2, "0")}</div>
            <div className="profile-label">
              <strong>{unit.name}</strong>
              <span>Water level {fmt(unit.water_level_m)} m · Invert {fmt(unit.invert_elevation_m)} m</span>
            </div>
            <div className="profile-bar-track">
              <div className="profile-bar" style={{ width: `${Math.max(8, (loss / maxLoss) * 100)}%` }} />
            </div>
            <strong className="profile-loss">-{fmt(loss)} m</strong>
          </div>
        );
      })}
    </div>
  );
}

function MassBalanceTable({ balance }) {
  const parameters = balance?.parameters || {};
  const rows = Object.values(parameters);
  if (!rows.length) return <div className="empty">No plant-wide mass balance available.</div>;

  return (
    <div className="data-table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            <th>Parameter</th>
            <th>Influent</th>
            <th>Influent Load</th>
            <th>Final</th>
            <th>Final Load</th>
            <th>Overall Removal</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.parameter}>
              <td><strong>{row.parameter}</strong></td>
              <td>{fmt(row.influent_concentration_mg_l)} mg/L</td>
              <td>{fmt(row.influent_load_kg_day)} kg/d</td>
              <td>{fmt(row.final_concentration_mg_l)} mg/L</td>
              <td>{fmt(row.final_load_kg_day)} kg/d</td>
              <td>{fmt(row.overall_removal_percent)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function MassBalanceFlow({ balance }) {
  const bod = balance?.parameters?.BOD;
  const tss = balance?.parameters?.TSS;
  const stages = bod?.streams || [];
  if (!stages.length) return null;

  return (
    <div className="balance-flow">
      {stages.map((stage, index) => {
        const tssPoint = tss?.streams?.[index];
        return (
          <div className="balance-stage" key={`${stage.stage}-${index}`}>
            <div className="balance-stage-number">{String(index + 1).padStart(2, "0")}</div>
            <strong>{stage.stage}</strong>
            <span>BOD {fmt(stage.concentration_mg_l)} mg/L</span>
            {tssPoint && <span>TSS {fmt(tssPoint.concentration_mg_l)} mg/L</span>}
            {index < stages.length - 1 && <div className="balance-arrow">→</div>}
          </div>
        );
      })}
    </div>
  );
}

function DataTable({ data }) {
  const rows = flattenObject(data);

  if (!rows.length) {
    return <div className="empty">No data available.</div>;
  }

  return (
    <div className="data-table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            <th>Parameter</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              <td>{row.label}</td>
              <td>
                {typeof row.value === "number"
                  ? fmt(row.value)
                  : String(row.value)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}


function StatusBadge({ status }) {
  const good = status === "PASS" || status === "DESIGN READY";
  return <span className={`status-pill ${good ? "good" : "review"}`}>{status}</span>;
}

function RemovalBars({ balance }) {
  const parameters = balance?.parameters || {};
  const rows = Object.values(parameters).filter((item) => item?.parameter);
  if (!rows.length) return <div className="empty">No mass-balance data available.</div>;
  return (
    <div className="removal-bars">
      {rows.map((item) => {
        const value = Math.max(0, Math.min(100, num(item.overall_removal_percent)));
        return (
          <div className="removal-row" key={item.parameter}>
            <div className="removal-label"><strong>{item.parameter}</strong><span>{fmt(value)}%</span></div>
            <div className="bar-track"><div className="bar-fill" style={{ width: `${value}%` }} /></div>
          </div>
        );
      })}
    </div>
  );
}

function UnitDesignGrid({ design }) {
  const units = [
    ["Screening", design?.preliminary_treatment?.screening],
    ["Grit Chamber", design?.preliminary_treatment?.grit],
    ["Primary Clarifier", design?.primary_treatment],
    ["Biological Reactor", design?.biological_treatment?.biological],
    ["Aeration System", design?.biological_treatment?.aeration],
    ["Secondary Clarifier", design?.secondary_treatment],
    ["Filtration", design?.tertiary_treatment?.filtration],
    ["Disinfection", design?.disinfection],
  ];
  return (
    <div className="unit-design-grid">
      {units.map(([name, data]) => {
        const rows = flattenObject(data).filter((r) => typeof r.value === "number").slice(0, 7);
        return (
          <article className="unit-card" key={name}>
            <div className="unit-card-head"><span>UNIT DESIGN</span><h3>{name}</h3></div>
            {rows.length ? rows.map((row) => (
              <div className="unit-metric" key={row.label}><span>{row.label.split(" / ").pop()}</span><strong>{fmt(row.value, 2)}</strong></div>
            )) : <div className="empty">No detailed output returned.</div>}
          </article>
        );
      })}
    </div>
  );
}

function App() {
  const [form, setForm] = useState(emptyForm);
  const [design, setDesign] = useState(null);
  const [savedProjects, setSavedProjects] = useState(() => loadSavedProjects());
  const [libraryOpen, setLibraryOpen] = useState(false);
  const [apiStatus, setApiStatus] = useState("checking");
  const [activeTab, setActiveTab] = useState("overview");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    fetch(`${API}/health`)
      .then((response) => {
        if (!response.ok) throw new Error("Backend unavailable");
        return response.json();
      })
      .then(() => !cancelled && setApiStatus("online"))
      .catch(() => !cancelled && setApiStatus("offline"));
    return () => { cancelled = true; };
  }, []);

  const update = (key, value) => {
    setForm((old) => ({
      ...old,
      [key]: value,
    }));
  };

  const submitDesign = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");

    const required = [
      ["project_name", "Project name"],
      ["wastewater_type", "Wastewater type"],
      ["average_flow_m3_day", "Average flow"],
      ["peak_flow_m3_day", "Peak flow"],
      ["influent_bod_mg_l", "Influent BOD"],
      ["influent_cod_mg_l", "Influent COD"],
      ["influent_tss_mg_l", "Influent TSS"],
      ["target_bod_mg_l", "Target BOD"],
      ["target_tss_mg_l", "Target TSS"],
    ];
    const missing = required.filter(([key]) => form[key] === "" || form[key] == null);
    if (missing.length) {
      setError(`Complete the required design-basis fields: ${missing.map(([, label]) => label).join(", ")}.`);
      setLoading(false);
      return;
    }

    try {
      const payload = {
        ...form,
        average_flow_m3_day: num(form.average_flow_m3_day),
        peak_flow_m3_day: num(form.peak_flow_m3_day),
        influent_bod_mg_l: num(form.influent_bod_mg_l),
        influent_cod_mg_l: num(form.influent_cod_mg_l),
        influent_tss_mg_l: num(form.influent_tss_mg_l),
        ammonia_mg_l: num(form.ammonia_mg_l),
        target_bod_mg_l: num(form.target_bod_mg_l),
        target_tss_mg_l: num(form.target_tss_mg_l),
      };

      const response = await fetch(`${API}/api/design`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const text = await response.text();

      if (!response.ok) {
        throw new Error(
          `Design API returned ${response.status}: ${text}`
        );
      }

      const result = JSON.parse(text);
      setDesign(result);
      setActiveTab("overview");
      const record = {
        id: `${Date.now()}`,
        name: result.project?.name || form.project_name,
        wastewater_type: form.wastewater_type,
        updated_at: new Date().toISOString(),
        form: clone(form),
        design: result,
      };
      const next = [record, ...savedProjects.filter((item) => item.name !== record.name)];
      setSavedProjects(next);
      saveSavedProjects(next);
    } catch (err) {
      setError(err.message || "Unable to generate design.");
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setForm(emptyForm);
    setDesign(null);
    setError("");
    setActiveTab("overview");
    setLibraryOpen(false);
  };

  const loadProject = (project) => {
    setForm(clone(project.form));
    setDesign(project.design || null);
    setError("");
    setActiveTab("overview");
    setLibraryOpen(false);
  };

  const loadTemplate = (type) => {
    setForm(clone(templates[type]));
    setDesign(null);
    setError("");
    setLibraryOpen(false);
  };

  const deleteProject = (id) => {
    const next = savedProjects.filter((item) => item.id !== id);
    setSavedProjects(next);
    saveSavedProjects(next);
  };

  const exportBasis = () => {
    downloadJson(form, `${safeFileName(form.project_name || "wwtp-design-basis")}-basis.json`);
  };

  const importInputRef = useRef(null);

  const importBasis = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const parsed = JSON.parse(reader.result);
        setForm({ ...emptyForm, ...parsed });
        setDesign(null);
        setError("");
      } catch {
        setError("Could not import the selected JSON design basis.");
      }
    };
    reader.readAsText(file);
    event.target.value = "";
  };

  const exportDesign = () => {
    if (!design) return;
    downloadJson(design, `${safeFileName(design.project?.name)}-design.json`);
  };

  const printReport = () => window.print();

  const designBasis = design?.design_basis || {};
  const flow = design?.flow || {};
  const loads = design?.loads || {};
  const process = design?.process_selection || {};
  const train = design?.treatment_train || {};
  const finalEffluent = design?.final_effluent || {};
  const utilities = design?.utilities || {};
  const metadata = design?.metadata || {};
  const engineeringChecksData = design?.engineering_checks || {};

  const engineeringChecks = useMemo(() => {
    const avg = num(designBasis.average_flow_m3_day);
    const peak = num(designBasis.peak_flow_m3_day);
    const bod = num(designBasis.influent_bod_mg_l);
    const cod = num(designBasis.influent_cod_mg_l);
    const tss = num(designBasis.influent_tss_mg_l);
    const targetBod = num(designBasis.target_bod_mg_l);
    const targetTss = num(designBasis.target_tss_mg_l);
    const ammonia = num(designBasis.ammonia_mg_l);
    const nitrification = Boolean(designBasis.nitrification_required);

    return [
      {
        label: "Peak flow ≥ average flow",
        pass: peak >= avg && avg > 0,
        detail: `${fmt(peak, 0)} / ${fmt(avg, 0)} m³/day`,
      },
      {
        label: "COD ≥ BOD",
        pass: cod >= bod,
        detail: `${fmt(cod, 0)} / ${fmt(bod, 0)} mg/L`,
      },
      {
        label: "Target BOD ≤ influent BOD",
        pass: targetBod <= bod,
        detail: `${fmt(targetBod)} / ${fmt(bod)} mg/L`,
      },
      {
        label: "Target TSS ≤ influent TSS",
        pass: targetTss <= tss,
        detail: `${fmt(targetTss)} / ${fmt(tss)} mg/L`,
      },
      {
        label: "Nitrification basis is defined",
        pass: !nitrification || ammonia > 0,
        detail: nitrification ? `${fmt(ammonia)} mg/L NH₃-N` : "Not required",
      },
    ];
  }, [designBasis]);

  const treatmentStages = Array.isArray(train.stages) ? train.stages : [];
  const checkTotal = num(engineeringChecksData.total_checks, engineeringChecks.length);
  const checkPassed = num(engineeringChecksData.pass_count, engineeringChecks.filter((c) => c.pass).length);
  const designScore = checkTotal ? Math.round((checkPassed / checkTotal) * 100) : 0;

  const tabs = useMemo(
    () => [
      ["overview", "Overview"],
      ["process", "Process Flow"],
      ["units", "Unit Design"],
      ["hydraulics", "Hydraulics"],
      ["biological", "Biological"],
      ["sludge", "Sludge"],
      ["utilities", "Utilities"],
      ["equipment", "Equipment"],
      ["mass-balance", "Mass Balance"],
      ["checks", "Design Checks"],
      ["assumptions", "Criteria & Assumptions"],
      ["calculations", "Raw Calculations"],
    ],
    []
  );

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">W</div>
          <div>
            <strong>WWTP ENGINE</strong>
            <span>Wastewater Treatment Plant Design Platform</span>
          </div>
        </div>

        <div className="top-status">
          <span className={`status-dot ${apiStatus}`} />
          {apiStatus === "online" ? "ENGINE ONLINE" : apiStatus === "offline" ? "ENGINE OFFLINE" : "CHECKING ENGINE"}
        </div>
      </header>

      <main className="layout">
        <aside className="sidebar">
          <div className="side-title">PROJECT DESIGN</div>

          <div className="side-step active">
            <b>01</b>
            <span>Design Basis</span>
          </div>

          <div className={`side-step ${design ? "active" : ""}`}>
            <b>02</b>
            <span>Process Design</span>
          </div>

          <div className={`side-step ${design ? "active" : ""}`}>
            <b>03</b>
            <span>Engineering Results</span>
          </div>

          <div className="side-info">
            <span>Engine</span>
            <strong>v{metadata.version || "0.2.0"}</strong>
          </div>
        </aside>

        <div className="content">
          <div className="page-header">
            <div>
              <p className="eyebrow">ENGINEERING DESIGN SYSTEM</p>
              <h1>WWTP Design Studio</h1>
              <p>
                Generate a complete wastewater treatment plant design
                from the design basis.
              </p>
            </div>

            {design && (
              <button className="secondary-btn" onClick={reset}>
                New Design
              </button>
            )}
          </div>

          {!design ? (
            <>
              <section className="workspace-intro">
                <div>
                  <p className="eyebrow">START A DESIGN</p>
                  <h2>Build from a clean design basis</h2>
                  <p>No values are pre-filled. Enter your own project data, reopen a saved project, import a basis, or use an explicitly labelled example template.</p>
                </div>
                <div className="workspace-actions">
                  <button type="button" className="secondary-btn" onClick={() => setLibraryOpen((value) => !value)}>
                    {libraryOpen ? "Hide Project Library" : "Open Project Library"}
                  </button>
                  <button type="button" className="secondary-btn" onClick={exportBasis}>Export Basis</button>
                  <button type="button" className="secondary-btn" onClick={() => importInputRef.current?.click()}>Import Basis</button>
                  <input ref={importInputRef} type="file" accept="application/json,.json" hidden onChange={importBasis} />
                </div>
              </section>

              {libraryOpen && (
                <section className="project-library">
                  <div className="library-header">
                    <div><h2>Project Library</h2><p>Saved projects are stored locally in this browser and can be reopened for review or reuse.</p></div>
                    <button type="button" className="secondary-btn" onClick={() => setLibraryOpen(false)}>Close</button>
                  </div>
                  <div className="template-grid">
                    <button type="button" className="template-card" onClick={() => loadTemplate("municipal")}>
                      <span>EXAMPLE TEMPLATE</span><strong>Municipal WWTP</strong><small>Typical municipal basis with nitrification.</small>
                    </button>
                    <button type="button" className="template-card" onClick={() => loadTemplate("industrial")}>
                      <span>EXAMPLE TEMPLATE</span><strong>Industrial WWTP</strong><small>Higher-strength industrial example basis.</small>
                    </button>
                  </div>
                  {savedProjects.length ? (
                    <div className="saved-project-list">
                      {savedProjects.map((project) => (
                        <div className="saved-project" key={project.id}>
                          <div><span>{project.wastewater_type?.toUpperCase()}</span><strong>{project.name}</strong><small>Updated {new Date(project.updated_at).toLocaleString()}</small></div>
                          <div className="saved-project-actions">
                            <button type="button" className="secondary-btn" onClick={() => loadProject(project)}>Open</button>
                            <button type="button" className="danger-btn" onClick={() => deleteProject(project.id)}>Delete</button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : <div className="empty library-empty">No saved projects yet. Generate a design and it will appear here automatically.</div>}
                </section>
              )}

              <form className="design-card" onSubmit={submitDesign}>
              <div className="card-header">
                <div>
                  <h2>Design Basis</h2>
                  <p>
                    Enter the fundamental hydraulic and pollutant
                    parameters.
                  </p>
                </div>
                <div className="badge">ENGINEERING INPUT</div>
              </div>

              <div className="form-section">
                <h3>Project</h3>
                <div className="form-grid">
                  <label>
                    Project Name
                    <input
                      value={form.project_name}
                      onChange={(e) =>
                        update("project_name", e.target.value)
                      }
                    />
                  </label>

                  <label>
                    Wastewater Type
                    <select
                      value={form.wastewater_type}
                      onChange={(e) => update("wastewater_type", e.target.value)}
                      required
                    >
                      <option value="">Select type…</option>
                      <option value="municipal">Municipal</option>
                      <option value="industrial">Industrial</option>
                    </select>
                  </label>
                </div>
              </div>

              <div className="form-section">
                <h3>Hydraulic Design</h3>
                <div className="form-grid">
                  <label>
                    Average Flow
                    <div className="input-unit">
                      <input
                        type="number"
                        value={form.average_flow_m3_day}
                        onChange={(e) =>
                          update(
                            "average_flow_m3_day",
                            e.target.value
                          )
                        }
                      />
                      <span>m³/day</span>
                    </div>
                  </label>

                  <label>
                    Peak Flow
                    <div className="input-unit">
                      <input
                        type="number"
                        value={form.peak_flow_m3_day}
                        onChange={(e) =>
                          update(
                            "peak_flow_m3_day",
                            e.target.value
                          )
                        }
                      />
                      <span>m³/day</span>
                    </div>
                  </label>
                </div>
              </div>

              <div className="form-section">
                <h3>Influent Quality</h3>
                <div className="form-grid four">
                  {[
                    ["influent_bod_mg_l", "BOD", "mg/L"],
                    ["influent_cod_mg_l", "COD", "mg/L"],
                    ["influent_tss_mg_l", "TSS", "mg/L"],
                    ["ammonia_mg_l", "Ammonia", "mg/L"],
                  ].map(([key, label, unit]) => (
                    <label key={key}>
                      {label}
                      <div className="input-unit">
                        <input
                          type="number"
                          value={form[key]}
                          onChange={(e) =>
                            update(key, e.target.value)
                          }
                        />
                        <span>{unit}</span>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              <div className="form-section">
                <h3>Effluent Requirements</h3>
                <div className="form-grid">
                  <label>
                    Target BOD
                    <div className="input-unit">
                      <input
                        type="number"
                        value={form.target_bod_mg_l}
                        onChange={(e) =>
                          update("target_bod_mg_l", e.target.value)
                        }
                      />
                      <span>mg/L</span>
                    </div>
                  </label>

                  <label>
                    Target TSS
                    <div className="input-unit">
                      <input
                        type="number"
                        value={form.target_tss_mg_l}
                        onChange={(e) =>
                          update("target_tss_mg_l", e.target.value)
                        }
                      />
                      <span>mg/L</span>
                    </div>
                  </label>
                </div>

                <label className="toggle-row">
                  <input
                    type="checkbox"
                    checked={form.nitrification_required}
                    onChange={(e) =>
                      update(
                        "nitrification_required",
                        e.target.checked
                      )
                    }
                  />
                  <span>
                    <strong>Nitrification Required</strong>
                    <small>
                      Include ammonia removal in biological design.
                    </small>
                  </span>
                </label>
              </div>

              {error && (
                <div className="error-box">
                  <strong>Design failed</strong>
                  <span>{error}</span>
                </div>
              )}

              <button className="generate-btn" disabled={loading}>
                {loading ? "CALCULATING DESIGN..." : "GENERATE WWTP DESIGN →"}
              </button>
            </form>
              </>
          ) : (
            <>
              <div className="result-hero">
                <div>
                  <p className="eyebrow">DESIGN COMPLETE</p>
                  <h2>{design.project?.name || "WWTP Design"}</h2>
                  <p>
                    {design.project?.wastewater_type || "Municipal"} wastewater
                    treatment plant
                  </p>
                </div>

                <div className="hero-actions">
                  <StatusBadge status={engineeringChecksData.status === "REVIEW REQUIRED" ? "REVIEW REQUIRED" : "DESIGN READY"} />
                  <button className="hero-btn" onClick={() => { setDesign(null); setError(""); window.scrollTo(0, 0); }}>Edit Basis</button>
                  <button className="hero-btn" onClick={printReport}>Print Report</button>
                  <button className="hero-btn" onClick={exportDesign}>Export JSON</button>
                </div>
              </div>

              <div className="metrics-grid">
                <Metric
                  label="Average Flow"
                  value={fmt(designBasis.average_flow_m3_day, 0)}
                  unit="m³/day"
                />
                <Metric
                  label="Peak Flow"
                  value={fmt(designBasis.peak_flow_m3_day, 0)}
                  unit="m³/day"
                />
                <Metric
                  label="Peak Factor"
                  value={fmt(designBasis.peak_factor)}
                  unit="×"
                />
                <Metric
                  label="Influent BOD"
                  value={fmt(designBasis.influent_bod_mg_l)}
                  unit="mg/L"
                />
                <Metric
                  label="Influent TSS"
                  value={fmt(designBasis.influent_tss_mg_l)}
                  unit="mg/L"
                />
                <Metric
                  label="Target BOD"
                  value={fmt(designBasis.target_bod_mg_l)}
                  unit="mg/L"
                />
              </div>

              <div className="command-strip">
                <div className="score-block"><span>DESIGN READINESS</span><strong>{designScore}%</strong><small>{checkPassed} of {checkTotal} engineering checks passed</small></div>
                <div className="command-item"><span>PROCESS</span><strong>{process.process_name || process.recommended_process || process.biological_process || "Selected"}</strong></div>
                <div className="command-item"><span>TRAIN</span><strong>{treatmentStages.length} treatment stages</strong></div>
                <div className="command-item"><span>ENERGY</span><strong>{fmt(utilities.energy?.daily_energy_kwh)} kWh/d</strong></div>
                <div className="command-item"><span>HEADLOSS</span><strong>{fmt(design.hydraulic_profile?.total_headloss_m)} m</strong></div>
              </div>

              <nav className="tabs">
                {tabs.map(([id, label]) => (
                  <button
                    key={id}
                    className={activeTab === id ? "tab active" : "tab"}
                    onClick={() => setActiveTab(id)}
                  >
                    {label}
                  </button>
                ))}
              </nav>

              {activeTab === "overview" && (
                <>
                  <Section
                    title="Design Overview"
                    subtitle="Key outputs from the complete engineering calculation."
                  >
                    <div className="overview-grid">
                      <div className="overview-card">
                        <span>Process Selection</span>
                        <strong>
                          {process.process_name ||
                            process.recommended_process ||
                            "Selected"}
                        </strong>
                      </div>

                      <div className="overview-card">
                        <span>Treatment Train</span>
                        <strong>
                          {Array.isArray(train.stages)
                            ? `${train.stages.length} stages`
                            : "Complete"}
                        </strong>
                      </div>

                      <div className="overview-card">
                        <span>Nitrification</span>
                        <strong>
                          {designBasis.nitrification_required
                            ? "Required"
                            : "Not Required"}
                        </strong>
                      </div>

                      <div className="overview-card">
                        <span>Final BOD Target</span>
                        <strong>
                          {fmt(finalEffluent.target_bod_mg_l ?? designBasis.target_bod_mg_l)} mg/L
                        </strong>
                      </div>
                    </div>
                  </Section>

                  <Section
                    title="Engineering Performance Snapshot"
                    subtitle="High-level outputs for rapid design review."
                  >
                    <div className="overview-grid engineering-kpis">
                      <div className="overview-card"><span>Overall BOD Removal</span><strong>{fmt(design.plant_mass_balance?.parameters?.BOD?.overall_removal_percent)}%</strong></div>
                      <div className="overview-card"><span>Overall TSS Removal</span><strong>{fmt(design.plant_mass_balance?.parameters?.TSS?.overall_removal_percent)}%</strong></div>
                      <div className="overview-card"><span>Total Headloss</span><strong>{fmt(design.hydraulic_profile?.total_headloss_m)} m</strong></div>
                      <div className="overview-card"><span>Estimated Energy</span><strong>{fmt(design.utilities?.energy?.daily_energy_kwh)} kWh/d</strong></div>
                    </div>
                  </Section>

                  <Section title="Pollutant Removal Profile" subtitle="Preliminary overall removal across the modeled treatment train.">
                    <RemovalBars balance={design.plant_mass_balance} />
                  </Section>

                  <Section
                    title="Design Basis"
                    subtitle="Inputs used by the design engine."
                  >
                    <DataTable data={designBasis} />
                  </Section>

                  <Section
                    title="Engineering Checks"
                    subtitle="Fast consistency checks on the submitted design basis. Detailed unit checks will be expanded in the engineering engine.">
                    <div className="check-summary">
                      <div><strong>{engineeringChecksData.pass_count ?? engineeringChecks.filter((c) => c.pass).length}</strong><span>Checks passed</span></div>
                      <div><strong>{engineeringChecksData.review_count ?? engineeringChecks.filter((c) => !c.pass).length}</strong><span>Need review</span></div>
                      <div><strong>{engineeringChecksData.total_checks ?? engineeringChecks.length}</strong><span>Total checks</span></div>
                      <div className={`status-pill ${engineeringChecksData.status === "PASS" ? "good" : "review"}`}>{engineeringChecksData.status || "BASIS CHECK"}</div>
                    </div>
                    <div className="checks-grid">
                      {(engineeringChecksData.checks || engineeringChecks.map((check) => ({
                        label: check.label,
                        status: check.pass ? "PASS" : "REVIEW",
                        value: check.detail,
                      }))).map((check) => (
                        <div className={`check-card ${check.status === "PASS" ? "pass" : "fail"}`} key={check.label}>
                          <div className="check-icon">{check.status === "PASS" ? "✓" : "!"}</div>
                          <div>
                            <strong>{check.label}</strong>
                            <span>{check.criterion || check.value || check.detail}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </Section>
                </>
              )}

              {activeTab === "process" && (
                <>
                  <Section
                    title="Treatment Train"
                    subtitle="Recommended process configuration."
                  >
                    <div className="process-flow">
                      {treatmentStages.length ? (
                        treatmentStages.map((stage, index) => (
                          <div className="process-node" key={`${stage.sequence}-${stage.unit}`}>
                            <span>{String(stage.sequence ?? index + 1).padStart(2, "0")}</span>
                            <strong>{stage.unit}</strong>
                            {stage.purpose && <small>{stage.purpose}</small>}
                          </div>
                        ))
                      ) : (
                        <div className="empty">No treatment train stages returned by the engine.</div>
                      )}
                    </div>
                  </Section>

                  <Section title="Process Selection">
                    <DataTable data={process} />
                  </Section>

                  <Section title="Treatment Train Engine Output">
                    <DataTable data={train} />
                  </Section>

                  <Section title="Preliminary Treatment">
                    <DataTable data={design.preliminary_treatment} />
                  </Section>

                  <Section title="Primary Treatment">
                    <DataTable data={design.primary_treatment} />
                  </Section>
                </>
              )}

              {activeTab === "units" && (
                <Section title="Unit-by-Unit Preliminary Design" subtitle="Key calculated sizing outputs across the treatment train.">
                  <UnitDesignGrid design={design} />
                </Section>
              )}

              {activeTab === "hydraulics" && (
                <>
                  <Section title="Flow">
                    <DataTable data={flow} />
                  </Section>

                  <Section title="Hydraulic Loads">
                    <DataTable data={design.hydraulic_loads} />
                  </Section>

                  <Section title="Hydraulic Profile" subtitle="Preliminary hydraulic grade and headloss sequence through the process train.">
                    <div className="profile-summary">
                      <Metric label="Total Headloss" value={fmt(design.hydraulic_profile?.total_headloss_m)} unit="m" />
                      <Metric label="Final Water Level" value={fmt(design.hydraulic_profile?.final_water_level_m)} unit="m RL" />
                      <Metric label="Profile Units" value={fmt(design.hydraulic_profile?.units?.length || 0, 0)} unit="units" />
                    </div>
                    <ProfileChart profile={design.hydraulic_profile} />
                    <ArrayTable data={design.hydraulic_profile?.units} />
                  </Section>
                </>
              )}

              {activeTab === "biological" && (
                <>
                  <Section title="Biological Treatment">
                    <DataTable data={design.biological_treatment} />
                  </Section>

                  <Section title="Secondary Treatment">
                    <DataTable data={design.secondary_treatment} />
                  </Section>

                  <Section title="Final Effluent">
                    <DataTable data={finalEffluent} />
                  </Section>
                </>
              )}

              {activeTab === "sludge" && (
                <>
                  <Section title="Sludge Production">
                    <DataTable data={design.sludge_management?.production} />
                  </Section>

                  <Section title="Sludge Management">
                    <DataTable data={design.sludge_management?.design} />
                  </Section>
                </>
              )}

              {activeTab === "utilities" && (
                <Section
                  title="Plant Utilities"
                  subtitle="Mechanical, aeration, chemical and energy requirements."
                >
                  <DataTable data={utilities} />
                </Section>
              )}

              {activeTab === "equipment" && (
                <Section
                  title="Equipment Schedule"
                  subtitle="Major equipment generated from the design."
                >
                  <ArrayTable
                    data={design.equipment_schedule}
                    columns={[
                      { key: "equipment_id", label: "ID" },
                      { key: "process", label: "Process" },
                      { key: "equipment", label: "Equipment" },
                      { key: "quantity", label: "Qty" },
                      { key: "duty", label: "Duty" },
                      { key: "capacity", label: "Capacity" },
                      { key: "remarks", label: "Remarks" },
                    ]}
                  />
                </Section>
              )}

              {activeTab === "mass-balance" && (
                <>
                  <Section
                    title="Plant-Wide Mass Balance"
                    subtitle="Preliminary pollutant accounting from influent through major treatment stages."
                  >
                    <MassBalanceFlow balance={design.plant_mass_balance} />
                    <MassBalanceTable balance={design.plant_mass_balance} />
                  </Section>

                  <Section
                    title="Mass Balance Assumptions"
                    subtitle="Transparent preliminary assumptions used by the accounting model."
                  >
                    <ul className="assumption-list">
                      {(design.plant_mass_balance?.assumptions || []).map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </Section>

                  <Section title="Stage-Level BOD Balance">
                    <ArrayTable
                      data={design.plant_mass_balance?.parameters?.BOD?.streams}
                      columns={[
                        { key: "stage", label: "Stage" },
                        { key: "parameter", label: "Parameter" },
                        { key: "concentration_mg_l", label: "Concentration (mg/L)" },
                        { key: "load_kg_day", label: "Load (kg/d)" },
                        { key: "removal_from_previous_percent", label: "Stage Removal (%)" },
                      ]}
                    />
                  </Section>
                </>
              )}

              {activeTab === "checks" && (
                <>
                  <Section title="Engineering Readiness" subtitle="Review the automated design checks before treating the output as a final engineering design.">
                    <div className="readiness-panel"><div className="readiness-score">{designScore}<span>/100</span></div><div><strong>{engineeringChecksData.status || "REVIEW"}</strong><p>{engineeringChecksData.note || "Automated preliminary checks are complete."}</p></div></div>
                  </Section>
                  <Section title="Detailed Design Checks">
                    <ArrayTable data={engineeringChecksData.checks} columns={[{key:"label",label:"Check"},{key:"value",label:"Calculated"},{key:"unit",label:"Unit"},{key:"criterion",label:"Criterion"},{key:"status",label:"Status"}]} />
                  </Section>
                </>
              )}

              {activeTab === "assumptions" && (
                <>
                  <Section title="Design Criteria"><DataTable data={design.design_criteria} /></Section>
                  <Section title="Mass-Balance Assumptions"><ul className="assumption-list">{(design.plant_mass_balance?.assumptions || []).map((item) => <li key={item}>{item}</li>)}</ul></Section>
                  <Section title="Engineering Disclaimer"><div className="notice-box">This platform provides preliminary process design and decision support. Final design requires project-specific criteria, site data, survey levels, geotechnical information, pilot/jar-test data where applicable, applicable Indian standards and engineering review.</div></Section>
                </>
              )}

              {activeTab === "calculations" && (
                <>
                  <Section title="Engine Metadata" subtitle="Build and calculation-engine status.">
                    <DataTable data={metadata} />
                  </Section>
                  <Section title="Pollutant Loads">
                    <DataTable data={loads} />
                  </Section>

                  <Section title="Mass Balance">
                    <DataTable data={design.mass_balance} />
                  </Section>

                  <Section title="Plant Mass Balance Summary">
                    <MassBalanceTable balance={design.plant_mass_balance} />
                  </Section>

                  <Section title="Detailed Engineering Checks" subtitle={engineeringChecksData.note}>
                    <ArrayTable
                      data={engineeringChecksData.checks}
                      columns={[
                        { key: "label", label: "Check" },
                        { key: "value", label: "Calculated" },
                        { key: "unit", label: "Unit" },
                        { key: "criterion", label: "Criterion" },
                        { key: "status", label: "Status" },
                      ]}
                    />
                  </Section>

                  <Section title="Core Design Engine">
                    <DataTable data={design.core_design} />
                  </Section>
                </>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
