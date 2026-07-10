/**
 * VitalSense AI - Frontend Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('predictionForm');
    const clearBtn = document.getElementById('clearBtn');
    const resultsSection = document.getElementById('resultsSection');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const toast = document.getElementById('toast');
    const predictBtn = document.getElementById('predictBtn');

    // ── Form Submit ───────────────────────────────────────────
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Collect form data
        const formData = new FormData(form);
        const payload = {};

        // Vitals
        const vitalFields = ['age', 'gender', 'weight_kg', 'height_cm', 'body_temp_f',
            'bp_systolic', 'bp_diastolic', 'heart_rate', 'blood_sugar', 'oxygen_level'];
        vitalFields.forEach(field => {
            payload[field] = formData.get(field);
        });

        // Symptoms (checkboxes)
        const symptomCheckboxes = form.querySelectorAll('input[type="checkbox"]');
        symptomCheckboxes.forEach(cb => {
            payload[cb.name] = cb.checked;
        });

        // Validate required fields
        for (const field of vitalFields) {
            if (!payload[field] && field !== 'gender') {
                showToast(`Please fill in all required fields`, 'error');
                document.querySelector(`[name="${field}"]`)?.focus();
                return;
            }
        }

        // Show loading
        loadingOverlay.classList.add('active');
        predictBtn.disabled = true;

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            const result = await response.json();

            if (result.success) {
                displayResults(result);
                showToast('Prediction complete!', 'success');
            } else {
                showToast(result.error || 'Prediction failed', 'error');
            }
        } catch (err) {
            showToast('Network error. Please try again.', 'error');
            console.error(err);
        } finally {
            loadingOverlay.classList.remove('active');
            predictBtn.disabled = false;
        }
    });

    // ── Clear Form ────────────────────────────────────────────
    clearBtn.addEventListener('click', () => {
        form.reset();
        resultsSection.style.display = 'none';
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // ── Display Results ───────────────────────────────────────
    function displayResults(data) {
        // Update confidence ring
        const circle = document.getElementById('confidenceCircle');
        const circumference = 2 * Math.PI * 54; // 339.292
        const offset = circumference - (data.confidence_pct / 100) * circumference;

        // Reset animation
        circle.style.strokeDashoffset = circumference;

        // Update text
        document.getElementById('confidenceValue').textContent = `${data.confidence_pct}%`;
        document.getElementById('diseaseName').textContent = data.predicted_disease;
        document.getElementById('diseaseDescription').textContent = data.description;
        document.getElementById('adviceText').textContent = data.advice;

        // Update top 3
        const top3List = document.getElementById('top3List');
        top3List.innerHTML = '';

        data.top3.forEach((item, index) => {
            const isActive = index === 0;
            const div = document.createElement('div');
            div.className = `top3-item ${isActive ? 'active' : ''}`;
            div.innerHTML = `
                <span class="disease">${index + 1}. ${item.disease}</span>
                <div class="confidence-bar">
                    <div class="bar">
                        <div class="bar-fill" style="width: 0%"></div>
                    </div>
                    <span class="confidence-value">${item.confidence}%</span>
                </div>
            `;
            top3List.appendChild(div);

            // Animate bar fill after a small delay
            setTimeout(() => {
                div.querySelector('.bar-fill').style.width = `${item.confidence}%`;
            }, 100 + index * 100);
        });

        // Show results
        resultsSection.style.display = 'block';

        // Animate confidence ring
        requestAnimationFrame(() => {
            circle.style.strokeDashoffset = offset;
        });

        // Smooth scroll to results
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }

    // ── Toast Notification ────────────────────────────────────
    function showToast(message, type = 'error') {
        toast.textContent = message;
        toast.className = `toast ${type} show`;

        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
});
