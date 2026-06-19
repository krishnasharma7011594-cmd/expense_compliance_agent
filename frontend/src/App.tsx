import React, { useState, useEffect } from 'react';
import {
    Bot,
    Search,
    History,
    Settings as SettingsIcon,
    Plus,
    ShieldAlert,
    MoreHorizontal,
    ChevronRight,
    TrendingDown,
    Activity
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

// types
interface AuditResult {
    status: string;
    audit_report: string;
    txn_id?: string;
    metadata?: {
        threat_score: number;
        session_id: string;
    };
}

const App: React.FC = () => {
    const [merchant, setMerchant] = useState('');
    const [amount, setAmount] = useState('');
    const [category, setCategory] = useState('meals');
    const [description, setDescription] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<AuditResult | null>(null);
    const [history, setHistory] = useState<any[]>([]);
    const [policies, setPolicies] = useState<any[]>([]);
    const [stats, setStats] = useState({ total_spent: 0, total_saved: 0, compliant_count: 0, rejected_count: 0 });
    const [activeTab, setActiveTab] = useState('audit');

    useEffect(() => {
        refreshData();
    }, []);

    const refreshData = async () => {
        try {
            const [historyRes, statsRes, policiesRes] = await Promise.all([
                axios.get('/api/history'),
                axios.get('/api/stats'),
                axios.get('/api/policies')
            ]);
            setHistory(historyRes.data);
            setStats(statsRes.data);
            setPolicies(policiesRes.data);
        } catch (error) {
            console.error("Data fetch failed", error);
        }
    };

    const handleAudit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setResult(null);

        const formData = new FormData();
        formData.append('merchant', merchant);
        formData.append('amount', parseFloat(amount).toString());
        formData.append('category', category);
        formData.append('description', description);

        try {
            const response = await axios.post('/api/audit', formData);
            setResult(response.data);
            refreshData();
            setMerchant('');
            setAmount('');
            setDescription('');
        } catch (error) {
            console.error("Audit failed", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="app-container" style={{ display: 'flex', height: '100vh' }}>
            {/* Sidebar */}
            <aside className="glass-card" style={{
                width: '280px',
                height: 'calc(100vh - 40px)',
                margin: '20px',
                padding: '2rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '2rem'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div style={{
                        background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))',
                        padding: '0.5rem',
                        borderRadius: '0.75rem'
                    }}>
                        <Bot size={24} color="white" />
                    </div>
                    <h2 style={{ fontSize: '1.25rem', letterSpacing: '-0.5px' }}>ADK Auditor</h2>
                </div>

                <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', flex: 1 }}>
                    <SidebarLink icon={<Activity size={20} />} label="Live Audit" active={activeTab === 'audit'} onClick={() => setActiveTab('audit')} />
                    <SidebarLink icon={<History size={20} />} label="History" active={activeTab === 'history'} onClick={() => setActiveTab('history')} />
                    <SidebarLink icon={<Search size={20} />} label="Policies" active={activeTab === 'policies'} onClick={() => setActiveTab('policies')} />
                    <SidebarLink icon={<SettingsIcon size={20} />} label="Settings" active={activeTab === 'settings'} onClick={() => setActiveTab('settings')} />
                </nav>

                <div className="glass-card" style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>SYSTEM STATUS</div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--success)' }}></div>
                        <span style={{ fontSize: '0.875rem' }}>Gemini 1.5 Flash</span>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main style={{ flex: 1, padding: '20px', paddingLeft: 0, overflowY: 'auto' }}>
                <header style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '2rem',
                    padding: '1rem 0'
                }}>
                    <div>
                        <h1 style={{ fontSize: '2rem', marginBottom: '0.25rem' }}>Compliance Dashboard</h1>
                        <p style={{ color: 'var(--text-secondary)' }}>Real-time fiscal oversight and anomaly detection.</p>
                    </div>
                    <div style={{ display: 'flex', gap: '1rem' }}>
                        <div className="glass-card" style={{ padding: '0.75rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <TrendingDown size={18} color="var(--success)" />
                            <span style={{ fontWeight: 600 }}>${stats.total_saved.toFixed(2)} Saved</span>
                        </div>
                    </div>
                </header>

                <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '2rem' }}>
                    {/* Tab Switching Logic */}
                    <section>
                        {activeTab === 'audit' && (
                            <>
                                <div className="glass-card" style={{ padding: '2rem', marginBottom: '2rem' }}>
                                    <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                        <Plus size={20} color="var(--accent-blue)" /> New Submission
                                    </h3>
                                    <form onSubmit={handleAudit} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                                        <div style={{ gridColumn: 'span 2' }}>
                                            <label style={labelStyle}>Merchant Name</label>
                                            <input
                                                className="input-field"
                                                placeholder="e.g. OpenAI, Starbucks, Delta Airlines"
                                                value={merchant}
                                                onChange={(e) => setMerchant(e.target.value)}
                                                required
                                            />
                                        </div>
                                        <div>
                                            <label style={labelStyle}>Amount (USD)</label>
                                            <input
                                                className="input-field"
                                                type="number"
                                                step="0.01"
                                                placeholder="0.00"
                                                value={amount}
                                                onChange={(e) => setAmount(e.target.value)}
                                                required
                                            />
                                        </div>
                                        <div>
                                            <label style={labelStyle}>Category</label>
                                            <select
                                                className="input-field"
                                                value={category}
                                                onChange={(e) => setCategory(e.target.value)}
                                            >
                                                <option value="meals">Meals & Entertainment</option>
                                                <option value="travel">Business Travel</option>
                                                <option value="software">Software & SaaS</option>
                                                <option value="office">Office Supplies</option>
                                                <option value="other">Other</option>
                                            </select>
                                        </div>
                                        <div style={{ gridColumn: 'span 2' }}>
                                            <label style={labelStyle}>Description (Optional)</label>
                                            <textarea
                                                className="input-field"
                                                rows={3}
                                                placeholder="What was this expense for?"
                                                value={description}
                                                onChange={(e) => setDescription(e.target.value)}
                                            />
                                        </div>
                                        <div style={{ gridColumn: 'span 2', display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                                            <button type="submit" className="btn-primary" disabled={loading} style={{ flex: 1 }}>
                                                {loading ? 'Analyzing...' : 'Execute AI Audit'}
                                            </button>
                                        </div>
                                    </form>
                                </div>

                                <AnimatePresence>
                                    {result && (
                                        <motion.div
                                            initial={{ opacity: 0, y: 20 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            className="glass-card"
                                            style={{ padding: '2rem', borderLeft: `4px solid ${result.status === 'SUCCESS' ? 'var(--success)' : 'var(--error)'}` }}
                                        >
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                                                <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                                    Audit Verdict <span className={`badge badge-${result.status === 'SUCCESS' ? 'compliant' : 'rejected'}`}>{result.status}</span>
                                                </h3>
                                                <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>ID: {result.txn_id}</span>
                                            </div>
                                            <div style={{
                                                background: 'rgba(0,0,0,0.2)',
                                                padding: '1.5rem',
                                                borderRadius: '1rem',
                                                fontSize: '0.95rem',
                                                lineHeight: '1.6',
                                                whiteSpace: 'pre-wrap'
                                            }}>
                                                {result.audit_report}
                                            </div>
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </>
                        )}

                        {activeTab === 'history' && (
                            <div className="glass-card" style={{ padding: '2rem' }}>
                                <h3 style={{ marginBottom: '1.5rem' }}>Transaction History</h3>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                    {history.map((item, idx) => (
                                        <div key={idx} className="glass-card" style={{ padding: '1.25rem', background: 'rgba(255,255,255,0.01)' }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                                <span style={{ fontWeight: 600 }}>{item.merchant}</span>
                                                <span style={{ fontWeight: 700 }}>${item.amount.toFixed(2)}</span>
                                            </div>
                                            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>{item.date} • {item.id}</div>
                                            <div style={{ fontSize: '0.85rem', color: item.status === 'COMPLIANT' ? 'var(--success)' : 'var(--warning)' }}>
                                                Verdict: {item.status} — {item.reason}
                                            </div>
                                        </div>
                                    ))}
                                    {history.length === 0 && <p>No audits performed yet.</p>}
                                </div>
                            </div>
                        )}

                        {activeTab === 'policies' && (
                            <div className="glass-card" style={{ padding: '2rem' }}>
                                <h3 style={{ marginBottom: '1.5rem' }}>Policy Explorer</h3>
                                <div style={{ display: 'grid', gap: '1rem' }}>
                                    {policies.map((p, idx) => (
                                        <div key={idx} className="glass-card" style={{ padding: '1.5rem', background: 'rgba(0, 118, 255, 0.05)' }}>
                                            <h4 style={{ textTransform: 'uppercase', marginBottom: '0.5rem', color: 'var(--accent-blue)' }}>{p.category}</h4>
                                            <p style={{ fontSize: '0.9rem', lineHeight: '1.5' }}>{p.rule}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {activeTab === 'settings' && (
                            <div className="glass-card" style={{ padding: '2rem' }}>
                                <h3 style={{ marginBottom: '1.5rem' }}>System Settings</h3>
                                <div style={{ display: 'grid', gap: '1.5rem' }}>
                                    <div>
                                        <label style={labelStyle}>AI Model</label>
                                        <input className="input-field" disabled value="Gemini 1.5 Flash" />
                                    </div>
                                    <div>
                                        <label style={labelStyle}>Auto-Approval Limit</label>
                                        <input className="input-field" type="number" defaultValue="100" />
                                    </div>
                                    <div>
                                        <label style={labelStyle}>Connected User ID</label>
                                        <input className="input-field" disabled value="krishnasharma7011594-cmd" />
                                    </div>
                                    <button className="btn-primary" style={{ marginTop: '1rem' }}>Save Changes</button>
                                </div>
                            </div>
                        )}
                    </section>

                    {/* Right Column: Mini Stats & Insights */}
                    <section style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                        <div className="glass-card" style={{ padding: '1.5rem' }}>
                            <h4 style={{ marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <Activity size={18} /> Performance Overview
                            </h4>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                                <div className="glass-card" style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)', textAlign: 'center' }}>
                                    <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>{stats.compliant_count}</div>
                                    <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>COMPLIANT</div>
                                </div>
                                <div className="glass-card" style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)', textAlign: 'center' }}>
                                    <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--warning)' }}>{stats.rejected_count}</div>
                                    <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>FLAGGED</div>
                                </div>
                            </div>
                            <button onClick={() => setActiveTab('history')} style={{
                                width: '100%',
                                marginTop: '1.25rem',
                                padding: '0.75rem',
                                background: 'transparent',
                                border: '1px solid var(--glass-border)',
                                borderRadius: '0.75rem',
                                color: 'var(--text-secondary)',
                                cursor: 'pointer',
                                fontSize: '0.85rem'
                            }}>View Audit Logs</button>
                        </div>

                        <div className="glass-card" style={{ padding: '1.5rem', background: 'linear-gradient(135deg, rgba(0, 118, 255, 0.1), rgba(157, 0, 255, 0.1))' }}>
                            <h4 style={{ marginBottom: '1rem' }}>AI Agent Insight</h4>
                            <p style={{ fontSize: '0.875rem', color: '#e2e8f0', lineHeight: '1.5' }}>
                                {stats.rejected_count > 0
                                    ? `Automated auditing has flagged ${stats.rejected_count} transactions. Most common reason: "Exceeds daily meal cap".`
                                    : "No compliance issues detected in recent transactions. Corporate health is optimal."}
                            </p>
                            <div style={{ marginTop: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-blue)', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer' }}>
                                Refresh Insights <ChevronRight size={14} />
                            </div>
                        </div>
                    </section>
                </div>
            </main >
        </div >
    );
};

const SidebarLink: React.FC<{ icon: any, label: string, active?: boolean, onClick: () => void }> = ({ icon, label, active, onClick }) => (
    <div
        onClick={onClick}
        style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            padding: '0.75rem 1rem',
            borderRadius: '0.75rem',
            cursor: 'pointer',
            background: active ? 'rgba(0, 118, 255, 0.1)' : 'transparent',
            color: active ? 'var(--accent-blue)' : 'var(--text-secondary)',
            transition: 'all 0.2s',
            fontWeight: active ? 600 : 400
        }}
    >
        {icon}
        <span>{label}</span>
    </div>
);

const labelStyle: React.CSSProperties = {
    display: 'block',
    fontSize: '0.75rem',
    fontWeight: 600,
    color: 'var(--text-secondary)',
    marginBottom: '0.5rem',
    textTransform: 'uppercase'
};

export default App;
