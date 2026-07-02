import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, ChevronRight, Award, BrainCircuit, Activity, Download, Clock, Star, Code } from 'lucide-react';
import Cursor from './Cursor';

export default function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleRunEngine = async () => {
    if (!file) return;
    setLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('job_description', 'Looking for a senior AI engineer with deep knowledge in LLMs, RAG, and production system architecture.');

      const API_BASE = import.meta.env.VITE_API_URL || 'https://YOUR-LIVE-BACKEND-URL.onrender.com';
      const res = await fetch(`${API_BASE}/api/run_pipeline`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (data.status === 'success') {
        setResults(data.results);
      } else {
        alert(data.error || 'Pipeline failed.');
      }
    } catch (err) {
      console.error(err);
      alert('Error connecting to backend.');
    } finally {
      setLoading(false);
    }
  };

  const exportToCSV = () => {
    if (!results.length) return;
    const header = ['candidate_id', 'rank', 'score', 'reasoning'];
    const rows = results.map(r => {
      let reasoning = r.reasoning || '';
      // Perfect comma-escaping
      reasoning = reasoning.replace(/"/g, '""');
      return `${r.candidate_id},${r.rank},${r.score},"${reasoning}"`;
    });
    const csvContent = [header.join(','), ...rows].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'team_submission.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen relative selection:bg-primary/20 selection:text-primary">
      <Cursor />
      
      {/* Blueprint Grid Background */}
      <div className="absolute inset-0 z-0 opacity-5 pointer-events-none" 
           style={{ backgroundImage: 'linear-gradient(#2B3445 1px, transparent 1px), linear-gradient(90deg, #2B3445 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <div className="relative z-10 max-w-6xl mx-auto px-6 py-16">
        {/* Header */}
        <motion.header 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.22, 0.61, 0.36, 1] }}
          className="flex flex-col items-center justify-center text-center mb-20"
        >
          <div className="inline-flex items-center space-x-2 bg-surface border border-border px-4 py-1.5 rounded-full mb-6">
            <BrainCircuit size={16} className="text-primary" />
            <span className="text-xs font-semibold tracking-widest text-text-secondary uppercase">Enterprise Intelligence</span>
          </div>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-text-primary mb-6">
            EchoHire
          </h1>
          <p className="text-lg text-text-muted max-w-2xl">
            Deep Context Analysis and Behavioral Viability scoring. 
            Identify the absolute best talent instantly, free of noise and unresponsive profiles.
          </p>
        </motion.header>

        {/* Action Center */}
        {!results.length && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.2, ease: [0.22, 0.61, 0.36, 1] }}
            className="flex flex-col items-center justify-center max-w-xl mx-auto"
          >
            <div 
              onClick={() => fileInputRef.current?.click()}
              className="w-full h-48 glass-panel border border-border rounded-2xl flex flex-col items-center justify-center hover:border-primary/50 hover:bg-elevated transition-colors duration-300 mb-8 relative overflow-hidden group"
            >
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileChange} 
                accept=".json,.jsonl" 
                className="hidden" 
              />
              <Upload className="text-text-secondary group-hover:text-primary transition-colors duration-300 mb-4" size={32} />
              <p className="text-text-secondary font-medium">
                {file ? file.name : "Upload candidate dataset (JSON/JSONL)"}
              </p>
            </div>

            <button
              onClick={handleRunEngine}
              disabled={!file || loading}
              className={`px-8 py-4 rounded-xl font-semibold flex items-center space-x-2 transition-all duration-300 ${
                !file ? 'bg-surface text-text-muted border border-border' : 'bg-elevated text-primary border border-primary shadow-glow hover:bg-surface'
              }`}
            >
              <span>{loading ? 'Analyzing Dataset...' : 'Run EchoHire Engine'}</span>
              {!loading && <ChevronRight size={18} />}
            </button>
            
            {loading && (
              <div className="w-full max-w-md h-1 bg-surface mt-10 rounded-full overflow-hidden">
                <motion.div 
                  className="h-full bg-primary"
                  animate={{ x: ['-100%', '200%'] }}
                  transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
                  style={{ width: '50%' }}
                />
              </div>
            )}
          </motion.div>
        )}

        {/* Results Arena */}
        <AnimatePresence>
          {results.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease: [0.22, 0.61, 0.36, 1] }}
            >
              <div className="flex justify-between items-center mb-8">
                <h2 className="text-2xl font-bold text-gray-100">Ranked Top {results.length} Candidates</h2>
                <button
                  onClick={exportToCSV}
                  className="px-5 py-2.5 rounded-lg font-semibold flex items-center space-x-2 bg-primary/10 text-primary border border-primary/30 hover:bg-primary/20 hover:border-primary/50 transition-colors duration-300"
                >
                  <Download size={16} />
                  <span>Export Result to CSV</span>
                </button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                {results.map((candidate, idx) => {
                  const matchPercentage = Math.round((candidate.score ?? 0) * 100);
                  
                  const getBadgeStyles = (percentage) => {
                    if (percentage >= 80) return "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
                    if (percentage >= 50) return "bg-amber-500/10 text-amber-400 border border-amber-500/20";
                    return "bg-rose-500/10 text-rose-400 border border-rose-500/20";
                  };

                  return (
                  <motion.div 
                    key={candidate.candidate_id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: Math.min(idx * 0.02, 0.5), ease: [0.22, 0.61, 0.36, 1] }}
                    className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-6 flex flex-col relative overflow-hidden group transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl hover:shadow-emerald-900/20 hover:border-emerald-500/30"
                  >
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-emerald-500/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                    
                    <div className="flex justify-between items-start mb-5">
                      <div className="flex flex-col">
                        <span className="text-xs text-gray-400 mb-1 font-mono uppercase">ID: {candidate.candidate_id}</span>
                        <div className="flex items-center space-x-2">
                          <Award size={18} className="text-gray-300" />
                          <span className="text-lg font-semibold text-gray-100">Rank #{candidate.rank}</span>
                        </div>
                      </div>
                      <div className={`px-3 py-1 rounded-lg flex items-center shadow-lg ${getBadgeStyles(matchPercentage)}`}>
                        <Activity size={14} className="mr-1.5" />
                        <span className="font-bold">{matchPercentage}% Match</span>
                      </div>
                    </div>

                    {/* Data Density Badges */}
                    <div className="flex flex-wrap gap-2 mb-5">
                      <div className="flex items-center space-x-1.5 bg-black/20 border border-white/5 px-2.5 py-1 rounded-md">
                        <Star size={12} className="text-gray-500" />
                        <span className="text-xs text-gray-400">{candidate.yoe} YoE</span>
                      </div>
                      <div className="flex items-center space-x-1.5 bg-black/20 border border-white/5 px-2.5 py-1 rounded-md">
                        <Code size={12} className="text-gray-500" />
                        <span className="text-xs text-gray-400 truncate max-w-[120px]">{candidate.top_skill}</span>
                      </div>
                      <div className="flex items-center space-x-1.5 bg-black/20 border border-white/5 px-2.5 py-1 rounded-md">
                        <Clock size={12} className="text-gray-500" />
                        <span className="text-xs text-gray-400">Active: {candidate.last_active}</span>
                      </div>
                    </div>
                    
                    <div className="flex-1 mt-auto border-t border-white/10 pt-4">
                      <p className="text-gray-400 leading-relaxed text-sm">
                        {candidate.reasoning}
                      </p>
                    </div>
                  </motion.div>
                )})}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
