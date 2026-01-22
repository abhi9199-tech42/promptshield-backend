from sqlalchemy import func, text
from sqlalchemy.orm import Session
from .models import ActivityLog
from datetime import datetime, timedelta

def get_summary_stats(db: Session, user_id: int = None):
    query = db.query(ActivityLog)
    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)
        
    total_requests = query.count()
    
    # Aggregates
    stats = query.with_entities(
        func.sum(ActivityLog.raw_tokens),
        func.sum(ActivityLog.compressed_tokens),
        func.avg(ActivityLog.latency_ms)
    ).first()
    
    total_raw = stats[0] or 0
    total_compressed = stats[1] or 0
    avg_latency = stats[2] or 0.0
    
    tokens_saved = total_raw - total_compressed
    savings_percentage = (tokens_saved / total_raw * 100) if total_raw > 0 else 0.0
    
    return {
        "total_requests": total_requests,
        "total_tokens_saved": tokens_saved,
        "average_savings_percentage": round(savings_percentage, 2),
        "average_latency_ms": round(avg_latency, 2)
    }

def get_recent_history(db: Session, user_id: int = None, limit: int = 50):
    query = db.query(ActivityLog)
    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)
    return query.order_by(ActivityLog.created_at.desc()).limit(limit).all()

def get_time_series_stats(db: Session, user_id: int = None, days: int = 7):
    """
    Returns daily request counts and token usage for the last N days.
    Suitable for visualization charts.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    query = db.query(
        func.date(ActivityLog.created_at).label('date'),
        func.count(ActivityLog.id).label('count'),
        func.sum(ActivityLog.raw_tokens).label('raw_tokens'),
        func.sum(ActivityLog.compressed_tokens).label('compressed_tokens')
    ).filter(ActivityLog.created_at >= start_date)
    
    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)
        
    results = query.group_by(func.date(ActivityLog.created_at)).all()
    
    # Format for frontend chart (fill in missing dates if needed, but keeping it simple for now)
    data = []
    for r in results:
        data.append({
            "date": r.date,
            "requests": r.count,
            "raw_tokens": r.raw_tokens or 0,
            "compressed_tokens": r.compressed_tokens or 0,
            "savings": (r.raw_tokens or 0) - (r.compressed_tokens or 0)
        })
        
    return sorted(data, key=lambda x: x['date'])
