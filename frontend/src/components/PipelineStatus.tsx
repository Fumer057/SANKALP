'use client';

interface PipelineStage {
    stage: number;
    name: string;
    status: string;
    detail: string;
}

interface PipelineStatusProps {
    stages: PipelineStage[];
    currentStage: number;
}

const stageIcons: Record<number, string> = {
    1: '🔍',
    2: '📦',
    3: '🤖',
    4: '🌐',
    5: '✨',
};

export default function PipelineStatus({ stages, currentStage }: PipelineStatusProps) {
    return (
        <div className="pipeline-section animate-fade-in-up">
            <div className="pipeline-header">Pipeline Stages</div>
            <div className="pipeline-stages">
                {stages.map((stage) => {
                    const isCompleted = stage.stage < currentStage;
                    const isActive = stage.stage === currentStage;

                    return (
                        <div
                            key={stage.stage}
                            className={`stage-card ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}
                        >
                            <div className="stage-number">
                                <span className="stage-status-icon">
                                    {isCompleted ? '✓' : isActive ? '⟳' : stageIcons[stage.stage] || '○'}
                                </span>
                                Stage {stage.stage}
                            </div>
                            <div className="stage-name">{stage.name}</div>
                            <div className="stage-detail">{stage.detail}</div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
