// Blackhole Examination Application Engine & Student Educational Portal

class TestbookApp {
  constructor() {
    this.tests = [];
    this.currentTest = null;
    this.currentQIndex = 0;
    this.userAnswers = {}; // { qIndex: { selected: 'A', status: 'answered', marked: false, timeSpent: 0 } }
    this.timerInterval = null;
    this.timeRemaining = 0; // seconds
    this.totalDurationSeconds = 0;
    this.language = 'bilingual';
    this.calcValue = '0';
    this.calcResetOnNext = false;
    this.solFilter = 'all';

    // Auth & Multi-tenant State: invalidate legacy auto-login session
    if (localStorage.getItem('cgl_auth_token')) {
      localStorage.removeItem('cgl_auth_token');
    }
    this.token = localStorage.getItem('cgl_session_v3') || null;
    this.currentUser = null;
    this.pendingTestId = null;
    this.historyData = [];
    this.materialsLoaded = false;
    this.currentStudyTab = 'ga';
    this.userNotes = [];

    this.init();
  }

  async init() {
    await this.checkAuth();
    await this.loadTestsList();
    await this.loadHistory();
    this.setupGlobalEvents();
  }

  getAuthHeaders() {
    const headers = { 'Content-Type': 'application/json' };
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    return headers;
  }

  setupGlobalEvents() {
    document.addEventListener('click', (e) => {
      const wrap = document.getElementById('candidateProfileWrap');
      const drop = document.getElementById('profileDropdown');
      if (wrap && drop && !wrap.contains(e.target)) {
        drop.style.display = 'none';
      }
    });
  }

  // --- Authentication & User Management ---
  async checkAuth() {
    let authed = false;
    if (this.token) {
      try {
        const res = await fetch('/api/auth/me', { headers: this.getAuthHeaders() });
        const data = await res.json();
        if (data.authenticated && data.user) {
          this.currentUser = data.user;
          authed = true;
        } else {
          this.currentUser = null;
          this.token = null;
          localStorage.removeItem('cgl_session_v3');
        }
      } catch (e) {
        console.error('Auth verification error:', e);
        this.currentUser = null;
        this.token = null;
        localStorage.removeItem('cgl_session_v3');
      }
    } else {
      this.currentUser = null;
    }
    this.updateUserInterface();
  }

  updateUserInterface() {
    const guestControls = document.getElementById('authGuestControls');
    const profileWrap = document.getElementById('candidateProfileWrap');
    const clearHistoryBtn = document.getElementById('btnClearHistory');

    if (this.currentUser) {
      if (guestControls) guestControls.style.display = 'none';
      if (profileWrap) profileWrap.style.display = 'block';

      // Avatar & Names (Strictly privacy protected: never display personal names like Anshul Yadav)
      let displayName = this.currentUser.full_name || 'Candidate';
      if (/anshul/i.test(displayName) || /yadav/i.test(displayName) || this.currentUser.role === 'admin') {
        displayName = 'Candidate';
      }

      const initials = displayName
        .split(' ')
        .map(n => n[0])
        .slice(0, 2)
        .join('')
        .toUpperCase();

      const elAvatar = document.getElementById('candidateAvatar');
      if (elAvatar) elAvatar.innerText = initials || 'CA';
      const elName = document.getElementById('candidateName');
      if (elName) elName.innerText = displayName;
      const elExam = document.getElementById('candidateExam');
      if (elExam) elExam.innerText = this.currentUser.target_exam || 'SSC CGL 2026';

      const elDropName = document.getElementById('dropUserName');
      if (elDropName) elDropName.innerText = displayName;
      const elDropEmail = document.getElementById('dropUserEmail');
      let displayEmail = this.currentUser.email || '';
      if (/anshul/i.test(displayEmail)) {
        displayEmail = 'admin@cglstudy.com';
      }
      if (elDropEmail) elDropEmail.innerText = displayEmail;
      const elDropRole = document.getElementById('dropUserRole');
      if (elDropRole) elDropRole.innerText = (this.currentUser.role || 'STUDENT').toUpperCase();

      if (clearHistoryBtn) clearHistoryBtn.style.display = (this.historyData && this.historyData.length > 0) ? 'inline-block' : 'none';
    } else {
      if (guestControls) guestControls.style.display = 'flex';
      if (profileWrap) profileWrap.style.display = 'none';
      if (clearHistoryBtn) clearHistoryBtn.style.display = 'none';
    }

    if (this.tests && this.tests.length > 0) {
      this.renderTestCards();
    }
  }

  toggleProfileDropdown(forceState) {
    const drop = document.getElementById('profileDropdown');
    if (!drop) return;
    if (typeof forceState === 'boolean') {
      drop.style.display = forceState ? 'block' : 'none';
    } else {
      drop.style.display = drop.style.display === 'block' ? 'none' : 'block';
    }
  }

  openAuthModal(tab = 'login', infoMessage = null) {
    const modal = document.getElementById('authModal');
    if (modal) modal.style.display = 'flex';
    this.switchAuthTab(tab);
    const alertBox = document.getElementById('authAlertBox');
    if (alertBox) {
      if (infoMessage) {
        alertBox.className = 'auth-alert info';
        alertBox.innerText = infoMessage;
        alertBox.style.display = 'block';
      } else {
        alertBox.style.display = 'none';
      }
    }
  }

  closeAuthModal() {
    const modal = document.getElementById('authModal');
    if (modal) modal.style.display = 'none';
  }

  switchAuthTab(tab) {
    const loginTab = document.getElementById('authTabLogin');
    const regTab = document.getElementById('authTabRegister');
    const loginForm = document.getElementById('loginForm');
    const regForm = document.getElementById('registerForm');
    const title = document.getElementById('authModalTitle');

    if (tab === 'login') {
      loginTab.classList.add('active');
      regTab.classList.remove('active');
      loginForm.style.display = 'block';
      regForm.style.display = 'none';
      title.innerText = 'Student Sign In';
    } else {
      loginTab.classList.remove('active');
      regTab.classList.add('active');
      loginForm.style.display = 'none';
      regForm.style.display = 'block';
      title.innerText = 'Create Student Account';
    }
  }

  async handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;
    const alertBox = document.getElementById('authAlertBox');

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (data.error) {
        alertBox.className = 'auth-alert error';
        alertBox.innerText = data.error;
        alertBox.style.display = 'block';
        return;
      }
      this.token = data.token;
      this.currentUser = data.user;
      localStorage.setItem('cgl_session_v3', this.token);
      this.updateUserInterface();
      this.closeAuthModal();
      await this.loadHistory();
      if (this.pendingTestId) {
        const testToStart = this.pendingTestId;
        this.pendingTestId = null;
        await this.selectTest(testToStart);
      } else {
        const welcomeName = /anshul/i.test(this.currentUser.full_name) ? 'Candidate' : this.currentUser.full_name;
        alert(`Welcome back, ${welcomeName}!`);
      }
    } catch (err) {
      alertBox.className = 'auth-alert error';
      alertBox.innerText = 'Network error while logging in.';
      alertBox.style.display = 'block';
    }
  }

  async handleRegister(e) {
    e.preventDefault();
    const full_name = document.getElementById('regFullName').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    const target_exam = document.getElementById('regTargetExam').value;
    const password = document.getElementById('regPassword').value;
    const alertBox = document.getElementById('authAlertBox');

    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ full_name, email, target_exam, password })
      });
      const data = await res.json();
      if (data.error) {
        alertBox.className = 'auth-alert error';
        alertBox.innerText = data.error;
        alertBox.style.display = 'block';
        return;
      }
      this.token = data.token;
      this.currentUser = data.user;
      localStorage.setItem('cgl_session_v3', this.token);
      this.updateUserInterface();
      this.closeAuthModal();
      await this.loadHistory();
      if (this.pendingTestId) {
        const testToStart = this.pendingTestId;
        this.pendingTestId = null;
        await this.selectTest(testToStart);
      } else {
        alert(`Account created successfully! Welcome, ${this.currentUser.full_name}!`);
      }
    } catch (err) {
      alertBox.className = 'auth-alert error';
      alertBox.innerText = 'Network error while registering.';
      alertBox.style.display = 'block';
    }
  }

  async logoutUser() {
    if (confirm('Are you sure you want to log out?')) {
      try {
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: this.getAuthHeaders(),
          body: JSON.stringify({ token: this.token })
        });
      } catch (e) {}
      this.token = null;
      this.currentUser = null;
      localStorage.removeItem('cgl_session_v3');
      localStorage.removeItem('cgl_auth_token');
      this.updateUserInterface();
      this.toggleProfileDropdown(false);
      this.showDashboard();
      this.loadHistory();
    }
  }

  // --- Views Navigation Helpers ---
  hideAllViews() {
    const views = ['dashboardView', 'instructionsView', 'testInterfaceView', 'resultView', 'historyView', 'studyMaterialsView'];
    views.forEach(id => {
      const el = document.getElementById(id);
      if (el) el.style.display = 'none';
    });
    const headerTestInfo = document.getElementById('headerTestInfo');
    const headerTimer = document.getElementById('headerTimerSection');
    const calcBtn = document.getElementById('calcBtn');
    const langSelect = document.getElementById('langSelectorWrap');
    if (headerTestInfo) headerTestInfo.style.display = 'none';
    if (headerTimer) headerTimer.style.display = 'none';
    if (calcBtn) calcBtn.style.display = 'none';
    if (langSelect) langSelect.style.display = 'none';
  }

  setActiveNav(linkId) {
    document.querySelectorAll('.nav-link-btn').forEach(btn => btn.classList.remove('active'));
    const target = document.getElementById(linkId);
    if (target) target.classList.add('active');
  }

  showDashboard() {
    this.stopTimer();
    this.hideAllViews();
    document.getElementById('dashboardView').style.display = 'block';
    this.setActiveNav('navLinkTests');
    this.loadHistory();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  async showHistoryView() {
    this.stopTimer();
    this.hideAllViews();
    document.getElementById('historyView').style.display = 'block';
    this.setActiveNav('navLinkHistory');
    window.scrollTo({ top: 0, behavior: 'smooth' });
    await this.renderHistory();
  }

  async showStudyMaterialsView(subTab = 'ga') {
    this.stopTimer();
    this.hideAllViews();
    document.getElementById('studyMaterialsView').style.display = 'block';
    this.setActiveNav('navLinkMaterials');
    window.scrollTo({ top: 0, behavior: 'smooth' });
    if (!this.materialsLoaded) {
      await this.loadStudyMaterials();
    }
    this.switchStudyTab(subTab);
  }

  showAdminView() {
    this.showDashboard();
  }

  // --- Tests List & Dashboard Metrics ---
  async loadTestsList() {
    try {
      const res = await fetch('/api/tests');
      this.tests = await res.json();
      this.renderTestCards();
      const badge = document.getElementById('testListCountBadge');
      if (badge) badge.innerText = `${this.tests.length} Tests Available`;
      const statTotal = document.getElementById('statTotalTests');
      if (statTotal) statTotal.innerText = this.tests.length;
    } catch (err) {
      console.error('Error loading tests:', err);
    }
  }

  renderTestCards() {
    const grid = document.getElementById('testListGrid');
    if (!grid) return;
    grid.innerHTML = '';

    this.tests.forEach((t) => {
      const card = document.createElement('div');
      card.className = 'test-card';
      card.innerHTML = `
        <div class="test-card-top">
          <span class="test-card-category">${t.category || 'SSC CGL Tier-2'}</span>
          <h3 class="test-card-title">${t.title}</h3>
          <p class="test-card-desc">${t.subtitle || '25 Questions with Real-time Exam Timer & TCS Marking'}</p>
        </div>
        <div class="test-card-meta">
          <span>
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
            ${t.durationMinutes} Mins
          </span>
          <span>
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
            ${t.numQuestions} Questions
          </span>
          <span>
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
            ${t.numQuestions * (t.marksPerQuestion || 3)} Marks
          </span>
        </div>
        <div class="test-card-actions">
          <span class="test-past-score">+3.0 Correct / -1.0 Wrong</span>
          ${this.currentUser 
            ? `<button class="btn btn-primary" onclick="app.selectTest('${t.id}')">Start Test</button>`
            : `<button class="btn btn-primary" onclick="app.selectTest('${t.id}')" style="background:#2563eb; display:inline-flex; align-items:center; gap:6px;"><span>🔒</span> Sign In to Start</button>`
          }
        </div>
      `;
      grid.appendChild(card);
    });
  }

  async loadHistory() {
    if (!this.currentUser) {
      this.historyData = [];
      const countEl = document.getElementById('navHistoryCount');
      if (countEl) countEl.innerText = 0;
      const dropCountEl = document.getElementById('dropAttemptCount');
      if (dropCountEl) dropCountEl.innerText = 0;
      const statTestsAttempted = document.getElementById('statTestsAttempted');
      if (statTestsAttempted) statTestsAttempted.innerText = 0;
      const statAccuracy = document.getElementById('statAccuracy');
      if (statAccuracy) statAccuracy.innerText = '0%';
      const statAvgScore = document.getElementById('statAvgScore');
      if (statAvgScore) statAvgScore.innerText = '0%';
      const banner = document.getElementById('recentAttemptBanner');
      if (banner) banner.style.display = 'none';
      const clearBtn = document.getElementById('btnClearHistory');
      if (clearBtn) clearBtn.style.display = 'none';
      return;
    }

    try {
      const res = await fetch('/api/history', { headers: this.getAuthHeaders() });
      const history = await res.json();
      this.historyData = history || [];

      const countEl = document.getElementById('navHistoryCount');
      if (countEl) countEl.innerText = this.historyData.length;
      const dropCountEl = document.getElementById('dropAttemptCount');
      if (dropCountEl) dropCountEl.innerText = this.historyData.length;
      const clearBtn = document.getElementById('btnClearHistory');
      if (clearBtn) clearBtn.style.display = this.historyData.length > 0 ? 'inline-block' : 'none';

      if (this.historyData.length > 0) {
        document.getElementById('statTestsAttempted').innerText = this.historyData.length;
        const totalAccuracy = this.historyData.reduce((acc, h) => acc + (h.accuracy || 0), 0);
        const avgAcc = Math.round(totalAccuracy / this.historyData.length);
        document.getElementById('statAccuracy').innerText = `${avgAcc}%`;

        const totalScores = this.historyData.reduce((acc, h) => acc + (h.score || 0), 0);
        const totalMax = this.historyData.reduce((acc, h) => acc + (h.maxMarks || 75), 0);
        const avgScorePercent = Math.round((totalScores / (totalMax || 1)) * 100);
        document.getElementById('statAvgScore').innerText = `${avgScorePercent}%`;

        // Render Recent Attempt Banner
        const latest = this.historyData[this.historyData.length - 1];
        const banner = document.getElementById('recentAttemptBanner');
        if (banner && latest) {
          const dateStr = latest.timestamp ? new Date(latest.timestamp).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) : 'Recent';
          banner.style.display = 'block';
          banner.innerHTML = `
            <div style="background: #e6f7ff; border: 1px solid #91d5ff; border-radius: 8px; padding: 14px 18px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
              <div>
                <span style="background: #1890ff; color: #fff; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 4px; text-transform: uppercase;">Latest Attempt</span>
                <strong style="margin-left: 8px; font-size: 15px; color: #003a8c;">${latest.testTitle}</strong>
                <span style="color: #595959; font-size: 13px; margin-left: 8px;">(${dateStr}) — Score: <strong>${latest.score}/${latest.maxMarks || 75}</strong> (${latest.accuracy}% Accuracy)</span>
              </div>
              <div style="display: flex; gap: 10px;">
                <button class="btn btn-primary" onclick="app.reviewPastAttempt(${this.historyData.length - 1})" style="padding: 6px 14px; font-size: 13px;">Review Solutions ↗</button>
                <button class="btn btn-outline" onclick="app.showHistoryView()" style="padding: 6px 14px; font-size: 13px;">View All (${this.historyData.length})</button>
              </div>
            </div>
          `;
        }
      } else {
        document.getElementById('statTestsAttempted').innerText = 0;
        document.getElementById('statAccuracy').innerText = '0%';
        document.getElementById('statAvgScore').innerText = '0%';
        const banner = document.getElementById('recentAttemptBanner');
        if (banner) banner.style.display = 'none';
      }
    } catch (err) {
      console.log('No history available.');
    }
  }

  // --- Attempt History View Renderer ---
  async renderHistory() {
    const listContainer = document.getElementById('historyListContainer');
    if (!listContainer) return;

    if (!this.currentUser) {
      listContainer.innerHTML = `
        <div class="history-empty-card" style="border: 2px dashed #cbd5e1; padding: 48px 24px; text-align: center; background: #f8fafc; border-radius: 16px;">
          <div style="font-size: 48px; margin-bottom: 12px;">🔒</div>
          <h3 class="history-empty-title" style="font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 8px;">Your Test History is Private</h3>
          <p class="history-empty-text" style="color: #64748b; max-width: 500px; margin: 0 auto 24px; line-height: 1.6;">
            Sign in to your candidate account or register for free to track all your mock test attempts, scores, solutions, and analytics securely.
          </p>
          <div style="display: flex; justify-content: center; gap: 12px; flex-wrap: wrap;">
            <button class="btn btn-primary" onclick="app.openAuthModal('login')">Sign In to Blackhole</button>
            <button class="btn btn-outline" onclick="app.openAuthModal('register')">Create Free Account</button>
          </div>
        </div>
      `;
      const clearBtn = document.getElementById('btnClearHistory');
      if (clearBtn) clearBtn.style.display = 'none';
      return;
    }

    listContainer.innerHTML = '<div style="padding: 30px; text-align: center; color: #64748b;">Loading your attempt history...</div>';

    try {
      const res = await fetch('/api/history', { headers: this.getAuthHeaders() });
      const history = await res.json();
      this.historyData = history || [];

      const clearBtn = document.getElementById('btnClearHistory');
      if (clearBtn) clearBtn.style.display = this.historyData.length > 0 ? 'inline-block' : 'none';

      if (!history || history.length === 0) {
        listContainer.innerHTML = `
          <div class="history-empty-card">
            <div class="history-empty-icon">📝</div>
            <h3 class="history-empty-title">No Tests Attempted Yet</h3>
            <p class="history-empty-text">You haven't submitted any mock tests under this account yet. Pick any 25-question mock test to begin practicing!</p>
            <button class="btn btn-primary" onclick="app.showDashboard()">Browse Available Tests</button>
          </div>
        `;
        return;
      }

      listContainer.innerHTML = '';
      const reversedHistory = [...history].reverse();
      reversedHistory.forEach((att, rIdx) => {
        const actualIndex = history.length - 1 - rIdx;
        const card = document.createElement('div');
        card.className = 'history-card';

        const dateStr = att.timestamp ? new Date(att.timestamp).toLocaleString('en-IN', {
          day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
        }) : 'Recent Attempt';

        const maxM = att.maxMarks || 75;
        const scorePct = Math.round((att.score / maxM) * 100);
        const mins = Math.floor((att.timeSpentSeconds || 0) / 60);
        const secs = (att.timeSpentSeconds || 0) % 60;
        const isNeedsWork = scorePct < 60;

        card.innerHTML = `
          <div class="history-card-header">
            <div class="history-title-group">
              <h3>${att.testTitle || 'SSC CGL Mains Mock Test'}</h3>
              <div class="history-date-stamp">
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                Attempted on: ${dateStr}
              </div>
            </div>
            <div class="history-score-badge ${isNeedsWork ? 'needs-work' : ''}">
              <div class="history-score-main">${att.score} / ${maxM}</div>
              <div class="history-score-sub">${scorePct}% Marks (${att.accuracy || 0}% Accuracy)</div>
            </div>
          </div>

          <div class="history-metrics-grid">
            <div class="history-metric-item">
              <span class="val">${att.accuracy || 0}%</span>
              <span class="lbl">Accuracy</span>
            </div>
            <div class="history-metric-item">
              <span class="val">${att.attempted || 0} / 25</span>
              <span class="lbl">Attempted</span>
            </div>
            <div class="history-metric-item">
              <span class="val correct-val">✅ ${att.correct || 0}</span>
              <span class="lbl">Correct (+3)</span>
            </div>
            <div class="history-metric-item">
              <span class="val incorrect-val">❌ ${att.incorrect || 0}</span>
              <span class="lbl">Incorrect (-1)</span>
            </div>
            <div class="history-metric-item">
              <span class="val">⏱️ ${mins}m ${secs}s</span>
              <span class="lbl">Time Spent</span>
            </div>
          </div>

          <div class="history-card-actions" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div style="display:flex; gap:10px;">
              <button class="btn btn-outline" onclick="app.selectTest('${att.testId || 'cgl-mains-mock-01'}')">Re-attempt Test</button>
              <button class="btn btn-primary" onclick="app.reviewPastAttempt(${actualIndex})">Review Questions & Solutions ↗</button>
            </div>
            <button class="btn btn-outline" style="color:#ef4444; border-color:#fca5a5;" onclick="app.deleteAttempt('${att.attemptId}')" title="Permanently delete this attempt">
              🗑️ Delete Attempt
            </button>
          </div>
        `;
        listContainer.appendChild(card);
      });
    } catch (err) {
      listContainer.innerHTML = '<div style="color:red; padding: 20px;">Failed to load test history.</div>';
    }
  }

  async deleteAttempt(attemptId) {
    if (!attemptId) {
      alert('Attempt ID missing.');
      return;
    }
    if (!confirm('Are you sure you want to permanently delete this test attempt? This action cannot be undone.')) {
      return;
    }

    try {
      const res = await fetch(`/api/history/${encodeURIComponent(attemptId)}`, {
        method: 'DELETE',
        headers: this.getAuthHeaders()
      });
      const data = await res.json();
      if (res.ok) {
        alert('Test attempt successfully deleted.');
        await this.loadHistory();
        await this.renderHistory();
      } else {
        alert(data.error || 'Failed to delete test attempt.');
      }
    } catch (e) {
      console.error('Delete attempt error:', e);
      alert('Network error while deleting attempt.');
    }
  }

  async clearAllHistory() {
    if (!confirm('Are you sure you want to permanently delete ALL your test attempts? This will reset your score and accuracy statistics. This action cannot be undone.')) {
      return;
    }

    try {
      const res = await fetch('/api/history/clear', {
        method: 'POST',
        headers: this.getAuthHeaders()
      });
      const data = await res.json();
      if (res.ok) {
        alert('All test attempts cleared successfully.');
        await this.loadHistory();
        await this.renderHistory();
      } else {
        alert(data.error || 'Failed to clear history.');
      }
    } catch (e) {
      console.error('Clear history error:', e);
      alert('Network error while clearing history.');
    }
  }

  async adminPurgeAllData() {
    if (!this.currentUser || this.currentUser.role !== 'admin') {
      alert('Only administrators can perform data purge operations.');
      return;
    }
    const confirmed = prompt('DANGER: This will permanently delete ALL student test attempt records from both local SQLite and the Supabase cloud database.\\n\\nType "PURGE" to confirm:');
    if (confirmed !== 'PURGE') {
      alert('Purge operation cancelled.');
      return;
    }

    try {
      const res = await fetch('/api/admin/clear-all-data', {
        method: 'POST',
        headers: this.getAuthHeaders()
      });
      const data = await res.json();
      if (res.ok) {
        alert(`Data purge completed successfully! ${data.records_deleted || 0} records were deleted.`);
        await this.loadHistory();
        await this.loadAdminData();
      } else {
        alert(data.error || 'Failed to purge data.');
      }
    } catch (e) {
      console.error('Admin purge error:', e);
      alert('Network error while purging data.');
    }
  }

  async reviewPastAttempt(actualIndex) {
    try {
      const res = await fetch('/api/history', { headers: this.getAuthHeaders() });
      const history = await res.json();
      const attempt = history[actualIndex];
      if (!attempt) {
        alert('Attempt not found.');
        return;
      }

      let questions = attempt.questions;
      if (!questions || questions.length === 0) {
        const testRes = await fetch(`/api/tests/${attempt.testId || 'cgl-mains-mock-01'}`);
        const testData = await testRes.json();
        questions = (testData.questions || []).map((q, idx) => ({
          index: idx,
          question_en: q.question_en,
          question_hi: q.question_hi,
          topic: q.topic,
          exam: q.exam,
          options: q.options,
          userSelected: null,
          correctOption: q.correct,
          status: 'unattempted',
          marks: 0,
          solution: q.solution,
          trick: q.trick,
          timeSpent: 0
        }));
      }

      const totalQ = questions.length;
      const mins = Math.floor((attempt.timeSpentSeconds || 0) / 60);
      const secs = (attempt.timeSpentSeconds || 0) % 60;

      this.currentTest = { id: attempt.testId, title: attempt.testTitle };
      this.showResults({
        title: attempt.testTitle || 'SSC CGL Mains Mock Test',
        score: attempt.score,
        maxMarks: attempt.maxMarks || 75,
        percentage: Math.round((attempt.score / (attempt.maxMarks || 75)) * 100),
        accuracy: attempt.accuracy || 0,
        attemptedCount: attempt.attempted || 0,
        totalQ: totalQ,
        correctCount: attempt.correct || 0,
        incorrectCount: attempt.incorrect || 0,
        timeFormatted: `${mins}m ${secs}s`,
        questions: questions
      });

      if (attempt.timestamp) {
        const dStr = new Date(attempt.timestamp).toLocaleString('en-IN', {
          day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
        });
        const sub = document.getElementById('resAttemptTimestamp');
        if (sub) sub.innerText = `Attempted on: ${dStr} • Candidate Performance & Complete Solutions`;
      }
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      console.error('Error reviewing attempt:', err);
      alert('Failed to load past attempt details.');
    }
  }

  // --- Active Test Execution & Timer ---
  async selectTest(testId) {
    if (!this.currentUser) {
      this.pendingTestId = testId;
      this.openAuthModal('login', 'Please sign in or create a free candidate account before starting this mock test.');
      return;
    }

    try {
      const res = await fetch(`/api/tests/${testId}`, { headers: this.getAuthHeaders() });
      if (res.status === 401) {
        this.pendingTestId = testId;
        this.openAuthModal('login', 'Sign in required to access test content. Please log in.');
        return;
      }
      this.currentTest = await res.json();
      this.showInstructions();
    } catch (err) {
      alert('Failed to load test details.');
    }
  }

  showInstructions() {
    if (!this.currentUser) {
      this.openAuthModal('login', 'Please sign in before starting any test.');
      return;
    }
    if (!this.currentTest) return;
    this.hideAllViews();
    document.getElementById('instructionsView').style.display = 'flex';
    document.getElementById('instTestTitle').innerText = this.currentTest.title;
    document.getElementById('instTestSubtitle').innerText = this.currentTest.subtitle || '';
    document.getElementById('instTotalQuestions').innerText = this.currentTest.questions.length;
    document.getElementById('instDuration').innerText = `${this.currentTest.durationMinutes} Mins`;
    document.getElementById('instMaxMarks').innerText = `${this.currentTest.questions.length * (this.currentTest.marksPerQuestion || 3)} Marks`;
  }

  startTest() {
    if (!this.currentUser) {
      this.openAuthModal('login', 'Please sign in before starting any test.');
      return;
    }
    if (!document.getElementById('instAgreeCheck').checked) {
      alert('Please check the agreement box before proceeding.');
      return;
    }

    this.currentQIndex = 0;
    this.userAnswers = {};
    for (let i = 0; i < this.currentTest.questions.length; i++) {
      this.userAnswers[i] = {
        selected: null,
        status: i === 0 ? 'not-answered' : 'not-visited',
        marked: false,
        timeSpent: 0
      };
    }

    document.getElementById('headerTestInfo').style.display = 'flex';
    document.getElementById('headerTestTitle').innerText = this.currentTest.title;
    document.getElementById('headerTimerSection').style.display = 'flex';
    document.getElementById('calcBtn').style.display = 'flex';
    document.getElementById('langSelectorWrap').style.display = 'flex';
    document.getElementById('secQCount').innerText = `${this.currentTest.questions.length} Qs`;

    this.hideAllViews();
    document.getElementById('testInterfaceView').style.display = 'flex';

    this.totalDurationSeconds = (this.currentTest.durationMinutes || 35) * 60;
    this.timeRemaining = this.totalDurationSeconds;
    this.startTimer();

    this.renderPalette();
    this.loadQuestion(0);
  }

  startTimer() {
    this.stopTimer();
    this.updateTimerDisplay();
    this.timerInterval = setInterval(() => {
      if (this.timeRemaining > 0) {
        this.timeRemaining--;
        if (this.userAnswers[this.currentQIndex]) {
          this.userAnswers[this.currentQIndex].timeSpent++;
        }
        this.updateTimerDisplay();
      } else {
        this.stopTimer();
        alert('Time is up! Your test is being automatically submitted.');
        this.finalSubmitTest();
      }
    }, 1000);
  }

  stopTimer() {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }
  }

  updateTimerDisplay() {
    const mins = Math.floor(this.timeRemaining / 60);
    const secs = this.timeRemaining % 60;
    const str = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    const display = document.getElementById('timerDisplay');
    if (display) {
      display.innerText = str;
      if (this.timeRemaining < 300) {
        display.classList.add('warning');
      } else {
        display.classList.remove('warning');
      }
    }
  }

  setLanguage(lang) {
    this.language = lang;
    this.loadQuestion(this.currentQIndex);
  }

  loadQuestion(index) {
    this.currentQIndex = index;
    const q = this.currentTest.questions[index];
    if (!q) return;

    if (this.userAnswers[index].status === 'not-visited') {
      this.userAnswers[index].status = 'not-answered';
    }

    document.getElementById('currentQNumberBadge').innerText = `Question ${index + 1}`;
    document.getElementById('currentQTopicTag').innerText = q.topic || 'Quantitative Aptitude';
    document.getElementById('currentQExamTag').innerText = q.exam || 'SSC CGL Mains 2026';

    const isMarked = this.userAnswers[index].marked;
    document.getElementById('markReviewTopText').innerText = isMarked ? '★ Marked for Review' : '☆ Mark for Review';

    const enEl = document.getElementById('qTextEn');
    const hiEl = document.getElementById('qTextHi');

    if (this.language === 'en') {
      enEl.style.display = 'block';
      hiEl.style.display = 'none';
      enEl.innerText = q.question_en || q.question_hi;
    } else if (this.language === 'hi') {
      enEl.style.display = 'none';
      hiEl.style.display = 'block';
      hiEl.innerText = q.question_hi || q.question_en;
    } else {
      enEl.style.display = 'block';
      hiEl.style.display = 'block';
      enEl.innerText = q.question_en || '';
      hiEl.innerText = q.question_hi || '';
    }

    const optContainer = document.getElementById('optionsContainer');
    optContainer.innerHTML = '';
    const selected = this.userAnswers[index].selected;

    q.options.forEach(opt => {
      const isSelected = selected === opt.id;
      const row = document.createElement('div');
      row.className = `option-row ${isSelected ? 'selected' : ''}`;
      row.onclick = () => this.selectOption(opt.id);

      row.innerHTML = `
        <input type="radio" name="testOption" class="opt-radio" ${isSelected ? 'checked' : ''}>
        <span class="opt-letter">(${opt.id})</span>
        <span class="opt-text">${opt.text}</span>
      `;
      optContainer.appendChild(row);
    });

    document.getElementById('prevBtn').disabled = (index === 0);
    this.renderPalette();
  }

  selectOption(optId) {
    const qState = this.userAnswers[this.currentQIndex];
    qState.selected = optId;
    this.loadQuestion(this.currentQIndex);
  }

  clearResponse() {
    const qState = this.userAnswers[this.currentQIndex];
    qState.selected = null;
    qState.status = qState.marked ? 'marked' : 'not-answered';
    this.loadQuestion(this.currentQIndex);
  }

  saveAndNext() {
    const qState = this.userAnswers[this.currentQIndex];
    if (qState.selected) {
      qState.status = qState.marked ? 'marked-answered' : 'answered';
    } else {
      qState.status = qState.marked ? 'marked' : 'not-answered';
    }

    if (this.currentQIndex < this.currentTest.questions.length - 1) {
      this.loadQuestion(this.currentQIndex + 1);
    } else {
      this.renderPalette();
    }
  }

  markReviewAndNext() {
    const qState = this.userAnswers[this.currentQIndex];
    qState.marked = true;
    if (qState.selected) {
      qState.status = 'marked-answered';
    } else {
      qState.status = 'marked';
    }

    if (this.currentQIndex < this.currentTest.questions.length - 1) {
      this.loadQuestion(this.currentQIndex + 1);
    } else {
      this.renderPalette();
    }
  }

  toggleMarkReview() {
    const qState = this.userAnswers[this.currentQIndex];
    qState.marked = !qState.marked;
    if (qState.marked) {
      qState.status = qState.selected ? 'marked-answered' : 'marked';
    } else {
      qState.status = qState.selected ? 'answered' : 'not-answered';
    }
    this.loadQuestion(this.currentQIndex);
  }

  goToPrevQuestion() {
    if (this.currentQIndex > 0) {
      this.loadQuestion(this.currentQIndex - 1);
    }
  }

  renderPalette() {
    const grid = document.getElementById('paletteGrid');
    if (!grid) return;
    grid.innerHTML = '';

    let answered = 0, notAnswered = 0, notVisited = 0, marked = 0, markedAnswered = 0;

    for (let i = 0; i < this.currentTest.questions.length; i++) {
      const state = this.userAnswers[i];
      let statusClass = 'not-visited';

      if (state.status === 'answered') { statusClass = 'answered'; answered++; }
      else if (state.status === 'not-answered') { statusClass = 'not-answered'; notAnswered++; }
      else if (state.status === 'marked') { statusClass = 'marked'; marked++; }
      else if (state.status === 'marked-answered') { statusClass = 'marked-answered'; markedAnswered++; }
      else { notVisited++; }

      const btn = document.createElement('button');
      btn.className = `palette-btn ${statusClass} ${i === this.currentQIndex ? 'active' : ''}`;
      btn.innerText = i + 1;
      btn.onclick = () => this.loadQuestion(i);
      grid.appendChild(btn);
    }

    document.getElementById('countAnswered').innerText = answered;
    document.getElementById('countNotAnswered').innerText = notAnswered;
    document.getElementById('countNotVisited').innerText = notVisited;
    document.getElementById('countMarked').innerText = marked;
    document.getElementById('countMarkedAnswered').innerText = markedAnswered;
  }

  promptSubmitTest() {
    let answered = 0, notAnswered = 0, marked = 0, notVisited = 0;
    for (let i = 0; i < this.currentTest.questions.length; i++) {
      const s = this.userAnswers[i];
      if (s.status === 'answered' || s.status === 'marked-answered') answered++;
      else if (s.status === 'not-answered') notAnswered++;
      else if (s.status === 'marked') marked++;
      else notVisited++;
    }

    document.getElementById('modalTotalQ').innerText = this.currentTest.questions.length;
    document.getElementById('modalAnsQ').innerText = answered;
    document.getElementById('modalNotAnsQ').innerText = notAnswered;
    document.getElementById('modalMarkedQ').innerText = marked;
    document.getElementById('modalNotVisQ').innerText = notVisited;

    document.getElementById('submitModal').style.display = 'flex';
  }

  closeSubmitModal() {
    document.getElementById('submitModal').style.display = 'none';
  }

  finalSubmitTest() {
    this.closeSubmitModal();
    this.stopTimer();

    let score = 0, correctCount = 0, incorrectCount = 0, attemptedCount = 0, unattemptedCount = 0;
    const marksPerQ = this.currentTest.marksPerQuestion || 3;
    const negMarks = this.currentTest.negativeMarks || 1;
    const totalQ = this.currentTest.questions.length;
    const maxMarks = totalQ * marksPerQ;

    const evaluatedQuestions = [];

    this.currentTest.questions.forEach((q, idx) => {
      const userState = this.userAnswers[idx] || {};
      const userSelected = userState.selected;
      const isCorrect = userSelected && userSelected.toUpperCase() === q.correct.toUpperCase();
      const isAttempted = !!userSelected;

      let marksEarned = 0;
      let status = 'unattempted';

      if (isAttempted) {
        attemptedCount++;
        if (isCorrect) {
          correctCount++;
          marksEarned = marksPerQ;
          status = 'correct';
        } else {
          incorrectCount++;
          marksEarned = -negMarks;
          status = 'incorrect';
        }
      } else {
        unattemptedCount++;
      }

      score += marksEarned;

      evaluatedQuestions.push({
        index: idx,
        question_en: q.question_en,
        question_hi: q.question_hi,
        topic: q.topic,
        exam: q.exam,
        options: q.options,
        userSelected: userSelected,
        correctOption: q.correct,
        status: status,
        marks: marksEarned,
        solution: q.solution,
        trick: q.trick,
        timeSpent: userState.timeSpent || 0
      });
    });

    const accuracy = attemptedCount > 0 ? Math.round((correctCount / attemptedCount) * 100) : 0;
    const percentage = Math.round((score / maxMarks) * 100);
    const timeSpentTotal = this.totalDurationSeconds - this.timeRemaining;
    const timeMins = Math.floor(timeSpentTotal / 60);
    const timeSecs = timeSpentTotal % 60;

    // Send to backend with Auth header
    fetch('/api/submit', {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        testId: this.currentTest.id,
        testTitle: this.currentTest.title,
        timestamp: new Date().toISOString(),
        score,
        maxMarks,
        accuracy,
        attempted: attemptedCount,
        correct: correctCount,
        incorrect: incorrectCount,
        unattempted: unattemptedCount,
        timeSpentSeconds: timeSpentTotal,
        questions: evaluatedQuestions
      })
    }).then(() => this.loadHistory()).catch(err => console.error('Save result error:', err));

    this.showResults({
      title: this.currentTest.title,
      score,
      maxMarks,
      percentage,
      accuracy,
      attemptedCount,
      totalQ,
      correctCount,
      incorrectCount,
      timeFormatted: `${timeMins}m ${timeSecs}s`,
      questions: evaluatedQuestions
    });
  }

  showResults(res) {
    this.hideAllViews();
    document.getElementById('resultView').style.display = 'block';

    document.getElementById('resTestTitle').innerText = res.title;
    document.getElementById('resScoreVal').innerText = res.score;
    document.getElementById('resMaxMarks').innerText = res.maxMarks;
    document.getElementById('resPercentage').innerText = `${res.percentage}% Score`;

    document.getElementById('resAccuracy').innerText = `${res.accuracy}%`;
    document.getElementById('resAttempted').innerText = `${res.attemptedCount} / ${res.totalQ}`;
    document.getElementById('resCorrect').innerText = res.correctCount;
    document.getElementById('resIncorrect').innerText = res.incorrectCount;
    document.getElementById('resTimeTaken').innerText = res.timeFormatted;

    document.getElementById('filterAllCount').innerText = res.totalQ;
    document.getElementById('filterCorrectCount').innerText = res.correctCount;
    document.getElementById('filterIncorrectCount').innerText = res.incorrectCount;
    document.getElementById('filterUnattemptedCount').innerText = res.totalQ - res.attemptedCount;

    this.evaluatedQuestions = res.questions;
    this.filterSolutions('all');
  }

  filterSolutions(filter) {
    this.solFilter = filter;
    document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
    if (filter === 'all') document.querySelector('.filter-chip:nth-child(1)').classList.add('active');
    else if (filter === 'correct') document.querySelector('.chip-correct').classList.add('active');
    else if (filter === 'incorrect') document.querySelector('.chip-incorrect').classList.add('active');
    else if (filter === 'unattempted') document.querySelector('.chip-unattempted').classList.add('active');

    const container = document.getElementById('solutionsListArea');
    container.innerHTML = '';

    const filtered = (this.evaluatedQuestions || []).filter(q => filter === 'all' || q.status === filter);

    if (filtered.length === 0) {
      container.innerHTML = `<div style="padding: 30px; text-align: center; color: #64748b;">No questions match the filter "${filter}".</div>`;
      return;
    }

    filtered.forEach(q => {
      const card = document.createElement('div');
      card.className = `sol-card ${q.status}-card`;

      const correctOptObj = q.options.find(o => o.id === q.correctOption) || {};
      const userOptObj = q.options.find(o => o.id === q.userSelected) || null;

      card.innerHTML = `
        <div class="sol-meta">
          <span class="sol-q-title">Q${q.index + 1}. [${q.topic || 'Maths'}] • ${q.exam || 'SSC CGL'}</span>
          <span class="status-tag ${q.status}">${q.status.toUpperCase()} (${q.marks >= 0 ? '+' + q.marks : q.marks})</span>
        </div>
        <div class="sol-q-body">
          <div class="english-text">${q.question_en || ''}</div>
          <div class="hindi-text">${q.question_hi || ''}</div>
        </div>
        <div class="sol-answers-grid">
          <div><strong>Your Answer:</strong> ${userOptObj ? `(${userOptObj.id}) ${userOptObj.text}` : '<span class="text-muted">Not Attempted</span>'}</div>
          <div><strong>Correct Answer:</strong> <span class="text-success">(${correctOptObj.id}) ${correctOptObj.text}</span></div>
          <div><strong>Time Spent:</strong> ${q.timeSpent}s</div>
        </div>
        <div class="sol-explanation-box">
          <div class="sol-exp-title">Detailed Solution / विस्तृत व्याख्या:</div>
          <div class="sol-exp-text">${q.solution || 'Solution not available.'}</div>
          ${q.trick ? `<div class="trick-box"><strong>Smart Trick / GP TRICK:</strong> ${q.trick}</div>` : ''}
        </div>
      `;
      container.appendChild(card);
    });
  }

  reattemptCurrentTest() {
    if (this.currentTest && this.currentTest.id) {
      this.selectTest(this.currentTest.id);
    } else {
      this.showDashboard();
    }
  }

  // --- Study Materials & Personal Notes Management ---
  async loadStudyMaterials() {
    try {
      const res = await fetch('/api/study-materials');
      const data = await res.json();
      data.forEach(item => {
        if (item.id === 'mat_ga_plan') {
          const el = document.getElementById('gaPlanMarkdownContainer');
          if (el) el.innerHTML = this.renderMarkdown(item.content);
        } else if (item.id === 'mat_formula_vault') {
          const el = document.getElementById('formulaVaultMarkdownContainer');
          if (el) el.innerHTML = this.renderMarkdown(item.content);
        }
      });
      this.materialsLoaded = true;
    } catch (e) {
      console.error('Error loading study materials:', e);
    }
    await this.loadStudentNotes();
  }

  switchStudyTab(tab) {
    this.currentStudyTab = tab;
    document.querySelectorAll('.study-sub-tab').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.study-tab-content').forEach(c => c.style.display = 'none');

    if (tab === 'formula') {
      const btn = document.getElementById('tabBtnFormula');
      const content = document.getElementById('studyContentFormula');
      if (btn) btn.classList.add('active');
      if (content) content.style.display = 'block';
    } else if (tab === 'notes') {
      const btn = document.getElementById('tabBtnNotes');
      const content = document.getElementById('studyContentNotes');
      if (btn) btn.classList.add('active');
      if (content) content.style.display = 'block';
      this.loadStudentNotes();
    } else {
      // Default to GA Plan
      this.currentStudyTab = 'ga';
      const btn = document.getElementById('tabBtnGA');
      const content = document.getElementById('studyContentGA');
      if (btn) btn.classList.add('active');
      if (content) content.style.display = 'block';
    }
  }

  async loadStudentNotes() {
    const grid = document.getElementById('studentNotesGrid');
    if (!grid) return;

    if (!this.currentUser) {
      grid.innerHTML = `
        <div style="grid-column: 1/-1; padding: 40px; text-align: center; background:#fff; border-radius:10px; border:1px solid #e2e8f0;">
          <h3>Personal Notes Vault</h3>
          <p style="color:#64748b; margin:10px 0 16px;">Please sign in to create and save personal study notes and formula shortcuts permanently.</p>
          <button class="btn btn-primary" onclick="app.openAuthModal('login')">Sign In to View Notes</button>
        </div>
      `;
      return;
    }

    try {
      const res = await fetch('/api/notes', { headers: this.getAuthHeaders() });
      const notes = await res.json();
      this.userNotes = notes || [];

      const countEl = document.getElementById('userNotesCount');
      if (countEl) countEl.innerText = this.userNotes.length;

      if (this.userNotes.length === 0) {
        grid.innerHTML = `
          <div style="grid-column: 1/-1; padding: 40px; text-align: center; background:#fff; border-radius:10px; border:2px dashed #cbd5e1;">
            <h3>No Personal Notes Yet</h3>
            <p style="color:#64748b; margin:8px 0 16px;">Create your first personal study note for formulas, mistakes to avoid, or exam strategies.</p>
            <button class="btn btn-primary" onclick="app.openNoteModal()">+ Create Personal Note</button>
          </div>
        `;
        return;
      }

      grid.innerHTML = '';
      this.userNotes.forEach(n => {
        const card = document.createElement('div');
        card.className = 'note-card';
        const dateStr = n.updated_at ? new Date(n.updated_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '';
        card.innerHTML = `
          <div class="note-card-top">
            <span class="note-topic-tag">${n.topic || 'General'}</span>
            <h4 class="note-title">${n.title}</h4>
            <div class="note-snippet">${n.content}</div>
          </div>
          <div class="note-card-bottom">
            <span class="note-date">Updated: ${dateStr}</span>
            <div class="note-actions">
              <button class="btn-icon-sm" onclick="app.openNoteModal('${n.id}')">Edit</button>
              <button class="btn-icon-sm text-danger" onclick="app.deleteNote('${n.id}')">Delete</button>
            </div>
          </div>
        `;
        grid.appendChild(card);
      });
    } catch (e) {
      grid.innerHTML = '<div style="color:red; padding:20px;">Failed to load personal notes.</div>';
    }
  }

  openNoteModal(noteId = null) {
    if (!this.currentUser) {
      this.openAuthModal('login');
      return;
    }
    const modal = document.getElementById('noteModal');
    const titleInput = document.getElementById('noteTitleInput');
    const topicInput = document.getElementById('noteTopicInput');
    const contentInput = document.getElementById('noteContentInput');
    const idInput = document.getElementById('editNoteId');
    const modalTitle = document.getElementById('noteModalTitle');

    if (noteId) {
      const note = this.userNotes.find(n => n.id === noteId);
      if (note) {
        idInput.value = note.id;
        titleInput.value = note.title;
        topicInput.value = note.topic || 'Algebra';
        contentInput.value = note.content;
        modalTitle.innerText = 'Edit Study Note';
      }
    } else {
      idInput.value = '';
      titleInput.value = '';
      topicInput.value = 'Algebra';
      contentInput.value = '';
      modalTitle.innerText = 'Create Personal Study Note';
    }
    modal.style.display = 'flex';
  }

  closeNoteModal() {
    document.getElementById('noteModal').style.display = 'none';
  }

  async saveNote() {
    const id = document.getElementById('editNoteId').value;
    const title = document.getElementById('noteTitleInput').value.trim();
    const topic = document.getElementById('noteTopicInput').value;
    const content = document.getElementById('noteContentInput').value.trim();

    if (!title || !content) {
      alert('Please provide a note title and content.');
      return;
    }

    try {
      const res = await fetch('/api/notes', {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ id: id || undefined, title, topic, content })
      });
      const data = await res.json();
      if (data.status === 'success') {
        this.closeNoteModal();
        await this.loadStudentNotes();
      } else {
        alert('Failed to save note.');
      }
    } catch (e) {
      alert('Error saving note.');
    }
  }

  async deleteNote(noteId) {
    if (confirm('Are you sure you want to delete this study note?')) {
      try {
        await fetch(`/api/notes/${noteId}`, {
          method: 'DELETE',
          headers: this.getAuthHeaders()
        });
        await this.loadStudentNotes();
      } catch (e) {
        alert('Error deleting note.');
      }
    }
  }

  renderMarkdown(md) {
    if (!md) return '';
    let html = md
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/gim, '<em>$1</em>')
      .replace(/`([^`]+)`/gim, '<code>$1</code>')
      .replace(/^\s*-\s+(.*$)/gim, '<li>$1</li>')
      .replace(/\n\n/gim, '<p></p>');

    // Basic Table parsing
    if (html.includes('|')) {
      const lines = html.split('\n');
      let inTable = false;
      let tableHtml = '<div class="table-responsive"><table>';
      const newLines = [];

      for (let l of lines) {
        if (l.trim().startsWith('|') && l.trim().endsWith('|')) {
          if (!inTable) { inTable = true; tableHtml = '<div class="table-responsive"><table>'; }
          if (l.includes('---')) continue;
          const cells = l.split('|').filter(c => c.trim().length > 0);
          tableHtml += '<tr>' + cells.map(c => `<td>${c.trim()}</td>`).join('') + '</tr>';
        } else {
          if (inTable) {
            inTable = false;
            tableHtml += '</table></div>';
            newLines.push(tableHtml);
          }
          newLines.push(l);
        }
      }
      if (inTable) {
        tableHtml += '</table></div>';
        newLines.push(tableHtml);
      }
      html = newLines.join('\n');
    }
    return html;
  }

  // --- Administrator Portal ---
  async loadAdminData() {
    try {
      const [overviewRes, dbRes] = await Promise.all([
        fetch('/api/admin/overview', { headers: this.getAuthHeaders() }),
        fetch('/api/admin/db-status', { headers: this.getAuthHeaders() })
      ]);
      const overview = await overviewRes.json();
      const dbStatus = await dbRes.json();

      document.getElementById('adminTotalStudents').innerText = overview.total_students || 0;
      document.getElementById('adminTotalSubmissions').innerText = overview.total_submissions || 0;
      document.getElementById('adminAvgScore').innerText = overview.avg_score || 0;
      document.getElementById('adminAvgAcc').innerText = `${overview.avg_accuracy || 0}%`;

      const statusBadge = document.getElementById('adminDbStatusBadge');
      if (dbStatus.is_connected) {
        statusBadge.className = 'db-status-pill online';
        statusBadge.innerText = '● Supabase PostgreSQL Connected';
      } else if (dbStatus.supabase_configured) {
        statusBadge.className = 'db-status-pill warning';
        statusBadge.innerText = '● Supabase Configured (Unreachable)';
      } else {
        statusBadge.className = 'db-status-pill';
        statusBadge.innerText = '● Local SQLite Database Active';
      }

      // Render Students Table
      const studentTbody = document.getElementById('adminStudentsTableBody');
      const students = overview.students || [];
      document.getElementById('adminStudentsBadge').innerText = `${students.length} Students`;
      if (students.length === 0) {
        studentTbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:#64748b;">No students registered yet.</td></tr>';
      } else {
        studentTbody.innerHTML = students.map(s => `
          <tr>
            <td><strong>${s.full_name}</strong> ${s.role === 'admin' ? '<span class="drop-user-role" style="font-size:9px;">ADMIN</span>' : ''}</td>
            <td>${s.email}</td>
            <td>${s.target_exam || 'SSC CGL 2026'}</td>
            <td>${s.created_at ? new Date(s.created_at).toLocaleDateString() : 'N/A'}</td>
            <td><span class="badge-sample answered">${s.tests_taken || 0}</span></td>
            <td><strong>${s.highest_score !== null ? s.highest_score + ' / 75' : '-'}</strong></td>
          </tr>
        `).join('');
      }

      // Render Submissions Table
      const subTbody = document.getElementById('adminSubmissionsTableBody');
      const subs = overview.recent_submissions || [];
      if (subs.length === 0) {
        subTbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:#64748b;">No test submissions yet.</td></tr>';
      } else {
        subTbody.innerHTML = subs.map(sub => `
          <tr>
            <td><strong>${sub.user_name || 'Candidate'}</strong><br><small style="color:#64748b;">${sub.user_email || ''}</small></td>
            <td>${sub.test_title}</td>
            <td><strong class="text-success">${sub.score} / ${sub.max_marks || 75}</strong></td>
            <td>${sub.accuracy}%</td>
            <td>${Math.floor(sub.time_spent_seconds / 60)}m ${sub.time_spent_seconds % 60}s</td>
            <td>${new Date(sub.created_at).toLocaleString()}</td>
          </tr>
        `).join('');
      }
    } catch (e) {
      console.error('Error loading admin overview:', e);
    }
  }

  async saveSupabaseConfig() {
    const url = document.getElementById('adminSupaUrl').value.trim();
    const key = document.getElementById('adminSupaKey').value.trim();
    const msgBox = document.getElementById('adminDbSyncMessage');

    if (!url || !key) {
      alert('Please enter both Supabase Project URL and Key.');
      return;
    }

    msgBox.style.display = 'block';
    msgBox.innerText = 'Testing Supabase connection...';

    try {
      const res = await fetch('/api/admin/db-config', {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ supabase_url: url, supabase_key: key })
      });
      const data = await res.json();
      if (data.status === 'success') {
        msgBox.innerText = '✅ ' + data.message;
        msgBox.style.color = '#16a34a';
        await this.loadAdminData();
      } else {
        msgBox.innerText = '❌ ' + (data.error || 'Connection failed.');
        msgBox.style.color = '#dc2626';
      }
    } catch (e) {
      msgBox.innerText = '❌ Network error connecting to Supabase.';
      msgBox.style.color = '#dc2626';
    }
  }

  async syncDataToSupabase() {
    const msgBox = document.getElementById('adminDbSyncMessage');
    msgBox.style.display = 'block';
    msgBox.innerText = 'Synchronizing local records to Supabase PostgreSQL...';

    try {
      const res = await fetch('/api/admin/db-sync', {
        method: 'POST',
        headers: this.getAuthHeaders()
      });
      const data = await res.json();
      if (data.status === 'success') {
        msgBox.innerText = `✅ Sync Complete: ${data.synced} new records uploaded to Supabase cloud.`;
        msgBox.style.color = '#16a34a';
      } else {
        msgBox.innerText = `⚠️ ${data.message || 'Sync skipped. Check Supabase credentials.'}`;
        msgBox.style.color = '#b45309';
      }
    } catch (e) {
      msgBox.innerText = '❌ Sync failed.';
      msgBox.style.color = '#dc2626';
    }
  }

  downloadSupabaseSql() {
    window.open('/data/supabase_schema.sql', '_blank');
  }

  // --- Calculator & Custom Tests ---
  toggleCalculator() {
    const m = document.getElementById('calcModal');
    m.style.display = m.style.display === 'flex' ? 'none' : 'flex';
  }

  calcPress(val) {
    const screen = document.getElementById('calcScreen');
    if (val === 'C') {
      this.calcValue = '0';
    } else if (val === '=') {
      try {
        const clean = this.calcValue.replace(/[^0-9+\-*/().]/g, '');
        this.calcValue = String(eval(clean));
        this.calcResetOnNext = true;
      } catch (e) {
        this.calcValue = 'Error';
      }
    } else if (val === 'sqrt') {
      try {
        const num = parseFloat(this.calcValue);
        this.calcValue = String(Math.sqrt(num));
        this.calcResetOnNext = true;
      } catch (e) {
        this.calcValue = 'Error';
      }
    } else {
      if (this.calcValue === '0' || this.calcResetOnNext) {
        this.calcValue = val;
        this.calcResetOnNext = false;
      } else {
        this.calcValue += val;
      }
    }
    screen.value = this.calcValue;
  }

  openNewTestModal() {
    document.getElementById('newTestModal').style.display = 'flex';
  }

  closeNewTestModal() {
    document.getElementById('newTestModal').style.display = 'none';
  }

  async saveNewTest() {
    const jsonStr = document.getElementById('newTestJson').value.trim();
    const title = document.getElementById('newTestTitle').value.trim();
    const category = document.getElementById('newTestCategory').value.trim() || 'Custom';
    const duration = parseInt(document.getElementById('newTestDuration').value) || 35;

    let payload = null;
    if (jsonStr) {
      try {
        payload = JSON.parse(jsonStr);
      } catch (e) {
        alert('Invalid JSON! Please check syntax.');
        return;
      }
    } else {
      alert('Please provide test questions JSON.');
      return;
    }

    if (title) payload.title = title;
    if (category) payload.category = category;
    if (duration) payload.durationMinutes = duration;

    try {
      const res = await fetch('/api/save-test', {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.status === 'success') {
        alert('New test added successfully!');
        this.closeNewTestModal();
        this.loadTestsList();
      } else {
        alert('Failed to save test.');
      }
    } catch (e) {
      alert('Network error while saving test.');
    }
  }
}

const app = new TestbookApp();
