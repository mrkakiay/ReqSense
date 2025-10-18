from flask import render_template, request, redirect, url_for, flash
from src.models import Experience, db
from src.app import app
import json
from datetime import datetime, timezone

@app.route('/submit-experience', methods=['GET', 'POST'])
def submit_experience():
    if request.method == 'POST':
        try:
            # Validate required fields
            if not request.form.get('narrative_text'):
                flash('Experience description is required', 'error')
                return redirect(url_for('submit_experience'))
                
            if not request.form.get('impact_severity'):
                flash('Impact severity is required', 'error')
                return redirect(url_for('submit_experience'))
            
            experience = Experience(
                narrative_text=request.form['narrative_text'],
                current_workaround=request.form['current_workaround'],
                impact_severity=request.form['impact_severity'],
                context_tags=request.form['context_tags'].split(','),
                participants=json.loads(request.form['participants']),
                pain_points=json.loads(request.form['pain_points']),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            db.session.add(experience)
            db.session.commit()
            
            flash('Experience submitted successfully', 'success')
            return redirect(url_for('submit_experience'))
            
        except json.JSONDecodeError:
            flash('Invalid JSON data in participants or pain points', 'error')
            return redirect(url_for('submit_experience'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting experience: {str(e)}', 'error')
            return redirect(url_for('submit_experience'))
    
    return render_template('submit_experience.html')