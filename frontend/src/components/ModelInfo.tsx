'use client';

interface ModelInfoProps {
    model: {
        name: string;
        description: string;
        source: string;
        poly_count?: number;
        file_size_mb?: number;
        confidence_score?: number; // Made optional for safety
        validation_explanation?: string; // Made optional for safety
        is_fallback?: boolean;
        category?: string;
    };
    allCandidates: Array<{
        id: string;
        name: string;
        source: string;
        confidence_score?: number;
        url: string;
    }>;
    onSelectCandidate: (url: string) => void;
    selectedUrl: string;
}

function getConfidenceLevel(score: number): { level: string; color: string; label: string } {
    if (score >= 75) return { level: 'high', color: '#00D4AA', label: 'High Confidence' };
    if (score >= 50) return { level: 'medium', color: '#FFB347', label: 'Moderate Confidence' };
    return { level: 'low', color: '#FF6B6B', label: 'Low Confidence' };
}

export default function ModelInfo({ model, allCandidates, onSelectCandidate, selectedUrl }: ModelInfoProps) {
    // Default values for missing data to prevent crashes
    const safeScore = model?.confidence_score ?? 0;
    const safeExplanation = model?.validation_explanation ?? "Validation report generating...";
    const conf = getConfidenceLevel(safeScore);

    if (!model) return null;

    return (
        <div className="info-panel">
            <div className="info-card animate-fade-in-up">
                <div className="info-card-title">Selected Model</div>
                <div className="model-name">{model.name || "Unnamed Model"}</div>
                <div className="model-description">{model.description || "No description available."}</div>
                <div className="model-meta">
                    <div className="meta-item">
                        <span className="meta-label">Source</span>
                        <div className="flex flex-col">
                            <span className="meta-value">{model.source || "Unknown Source"}</span>
                        </div>
                    </div>
                    <div className="meta-item">
                        <span className="meta-label">Category</span>
                        <span className="meta-value" style={{ textTransform: 'capitalize' }}>
                            {model.category || 'General'}
                        </span>
                    </div>
                    {model.file_size_mb ? (
                        <div className="meta-item">
                            <span className="meta-label">File Size</span>
                            <span className="meta-value">{model.file_size_mb} MB</span>
                        </div>
                    ) : null}
                </div>
            </div>

            {/* Confidence Score */}
            <div className="info-card animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
                <div className="info-card-title">AI Confidence Score</div>
                <div className="confidence-meter">
                    <div className="confidence-score" style={{ color: conf.color }}>
                        {safeScore}%
                    </div>
                    <div className="confidence-bar-bg">
                        <div
                            className={`confidence-bar-fill ${conf.level}`}
                            style={{ width: `${safeScore}%` }}
                        />
                    </div>
                    <div className="confidence-label">{conf.label}</div>
                </div>
            </div>

            {/* Validation Explanation */}
            <div className="info-card animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                <div className="info-card-title">AI Validation Report</div>
                <div className="validation-text">{safeExplanation}</div>
            </div>

            {/* Candidates List */}
            {(allCandidates || []).length > 1 && (
                <div className="info-card animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
                    <div className="info-card-title">
                        All Candidates ({allCandidates.length})
                    </div>
                    {allCandidates.map((candidate, idx) => {
                        const cConf = getConfidenceLevel(candidate.confidence_score ?? 0);
                        return (
                            <div
                                key={candidate.id}
                                className={`candidate-item ${candidate.url === selectedUrl ? 'selected' : ''}`}
                                onClick={() => onSelectCandidate(candidate.url)}
                            >
                                <div className="candidate-rank">{idx + 1}</div>
                                <div className="candidate-info">
                                    <div className="candidate-name">{candidate.name || "Candidate"}</div>
                                    <div className="candidate-source">{candidate.source}</div>
                                </div>
                                <div className="candidate-score" style={{ color: cConf.color }}>
                                    {candidate.confidence_score ?? 0}%
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
