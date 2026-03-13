'use client';

interface ModelInfoProps {
    model: {
        name: string;
        description: string;
        source: string;
        poly_count?: number;
        file_size_mb?: number;
        confidence_score: number;
        validation_explanation: string;
        is_fallback?: boolean;
        category?: string;
    };
    allCandidates: Array<{
        id: string;
        name: string;
        source: string;
        confidence_score: number;
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
    const conf = getConfidenceLevel(model.confidence_score);

    return (
        <div className="info-panel">
            {/* Model Details */}
            <div className="info-card animate-fade-in-up">
                <div className="info-card-title">Selected Model</div>
                <div className="model-name">{model.name}</div>
                <div className="model-description">{model.description}</div>
                <div className="model-meta">
                    <div className="meta-item">
                        <span className="meta-label">Source</span>
                        <span className="meta-value">{model.source}</span>
                    </div>
                    <div className="meta-item">
                        <span className="meta-label">Category</span>
                        <span className="meta-value" style={{ textTransform: 'capitalize' }}>
                            {model.category || 'General'}
                        </span>
                    </div>
                    {model.poly_count ? (
                        <div className="meta-item">
                            <span className="meta-label">Polygons</span>
                            <span className="meta-value">{model.poly_count.toLocaleString()}</span>
                        </div>
                    ) : null}
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
                        {model.confidence_score}%
                    </div>
                    <div className="confidence-bar-bg">
                        <div
                            className={`confidence-bar-fill ${conf.level}`}
                            style={{ width: `${model.confidence_score}%` }}
                        />
                    </div>
                    <div className="confidence-label">{conf.label}</div>
                </div>
            </div>

            {/* Validation Explanation */}
            <div className="info-card animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                <div className="info-card-title">AI Validation Report</div>
                <div className="validation-text">{model.validation_explanation}</div>
            </div>

            {/* Candidates List */}
            {allCandidates.length > 1 && (
                <div className="info-card animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
                    <div className="info-card-title">
                        All Candidates ({allCandidates.length})
                    </div>
                    {allCandidates.map((candidate, idx) => {
                        const cConf = getConfidenceLevel(candidate.confidence_score);
                        return (
                            <div
                                key={candidate.id}
                                className={`candidate-item ${candidate.url === selectedUrl ? 'selected' : ''}`}
                                onClick={() => onSelectCandidate(candidate.url)}
                            >
                                <div className="candidate-rank">{idx + 1}</div>
                                <div className="candidate-info">
                                    <div className="candidate-name">{candidate.name}</div>
                                    <div className="candidate-source">{candidate.source}</div>
                                </div>
                                <div className="candidate-score" style={{ color: cConf.color }}>
                                    {candidate.confidence_score}%
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
