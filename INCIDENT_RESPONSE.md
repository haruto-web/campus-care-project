# Incident Response Plan (BrightTrack LMS)

## 1. Purpose

This document defines how the BrightTrack team prepares for, responds to, and learns from incidents that impact:

- availability (downtime, degraded performance),
- security (unauthorized access, suspicious activity, data exposure),
- integrity (tampering, unexpected data changes),
- critical workflows (login, OTP, messaging, class operations, wellness alerts).

## 2. Scope

This plan applies to:

- Application: Django app (`accounts`, `academics`, `wellness`, `messaging`, `ai_assistant`, `ml_models`)
- Infrastructure: Render deployment, PostgreSQL database
- Integrations: Cloudinary, Brevo email, Gemini API, Google OAuth
- Operational data: user accounts, audit logs, wellness/intervention records, messaging records

## 3. Incident Severity Levels

Use the highest matching level.

### SEV-1 (Critical)

- Full production outage
- Confirmed data breach or active compromise
- Unauthorized admin/superadmin access
- Data corruption affecting core records

Target response:

- Acknowledge and assign Incident Commander within 15 minutes
- Begin containment immediately

### SEV-2 (High)

- Major feature unavailable (login, OTP, messaging, wellness alerts)
- Severe performance degradation for many users
- Suspected security incident requiring urgent investigation

Target response:

- Acknowledge within 30 minutes
- Start mitigation within 60 minutes

### SEV-3 (Medium)

- Partial degradation or localized impact
- Non-critical integration failure with workaround
- Repeated errors without confirmed security impact

Target response:

- Acknowledge within 4 hours
- Mitigate within 1 business day

### SEV-4 (Low)

- Minor bug, cosmetic issue, low-risk anomaly

Target response:

- Track in backlog and schedule fix

## 4. Roles and Responsibilities

Minimum assignment for SEV-1/SEV-2:

- Incident Commander (IC): owns decision-making, timeline, and status updates
- Operations Lead: deployment/platform actions (Render, environment, rollback)
- App Lead: code-level diagnosis and fixes
- Security Lead: security triage, containment, evidence protection
- Communications Lead: stakeholder updates (internal/admin users)
- Scribe: incident log, timestamps, actions, outcomes

If team is small, one person can hold multiple roles, but IC must be explicitly designated.

## 5. Incident Response Lifecycle

### 5.1 Detect and Triage

Possible detection signals:

- user reports,
- elevated error rates,
- failed login/OTP anomalies,
- suspicious audit log entries,
- unusual admin actions,
- provider outages (Render/Brevo/Cloudinary/Gemini).

Immediate triage checklist:

1. What is affected?
2. Who is affected and how many users?
3. Is this ongoing?
4. Any sign of unauthorized access or data exposure?
5. Severity level (SEV-1 to SEV-4)?
6. Who is Incident Commander?

### 5.2 Contain

Containment goals:

- stop active harm,
- prevent spread,
- preserve evidence.

Containment examples:

- temporarily disable vulnerable endpoint/feature flag,
- rotate secrets/API keys if compromise suspected,
- invalidate active sessions for targeted accounts,
- restrict admin access,
- rate-limit or block abusive sources,
- pause risky background jobs.

### 5.3 Eradicate and Recover

1. Identify root cause (code, config, infra, third-party dependency, credentials).
2. Apply fix (patch, configuration change, rollback, database repair).
3. Verify critical flows:
   - login and OTP,
   - role-based access,
   - messaging send/receive/report,
   - wellness alert generation,
   - audit log writes and integrity checks.
4. Monitor for recurrence.
5. Officially close incident when stable.

### 5.4 Post-Incident Review

Complete within 5 business days for SEV-1/SEV-2.

Required outputs:

- timeline with timestamps,
- root cause,
- what worked / what failed,
- customer or admin impact summary,
- corrective actions with owners and due dates,
- prevention updates (tests, monitoring, hardening, runbooks).

## 6. Security-Specific Handling

If unauthorized access or breach is suspected:

1. Escalate immediately to SEV-1 until proven otherwise.
2. Preserve logs and evidence (do not delete records).
3. Rotate sensitive credentials:
   - `SECRET_KEY` (if exposure suspected),
   - database credentials,
   - Brevo, Cloudinary, Gemini, Google OAuth secrets.
4. Revoke suspicious sessions/tokens.
5. Validate integrity of critical records and audit chain.
6. Determine data exposure scope.
7. Prepare notification plan based on legal/organizational requirements.

## 7. Operational Runbooks (Quick Actions)

### 7.1 Full Outage

1. Confirm outage on production URL.
2. Check latest deployment and recent changes.
3. Roll back to last known good deploy if needed.
4. Validate DB connectivity and migration state.
5. Restore service, then run focused regression checks.

### 7.2 Login/OTP Failure

1. Check auth endpoints and error logs.
2. Validate OTP generation/verification and email provider health (Brevo).
3. Confirm environment variables and time-sensitive settings.
4. Apply hotfix or temporary fallback if safe.

### 7.3 Suspected Account Compromise

1. Lock or suspend affected account(s).
2. Force password reset and session invalidation.
3. Review audit logs for admin actions and unusual access patterns.
4. Re-enable after verification and credential reset.

### 7.4 Messaging Abuse or Dangerous Content

1. Triage reported content and related accounts.
2. Apply suspension controls according to policy.
3. Preserve message and moderation logs.
4. Confirm reporting and resolution audit entries are intact.

### 7.5 Data Integrity/Tamper Alert

1. Verify audit hash chain status.
2. Identify first inconsistent record/time.
3. Isolate write paths and recent privileged actions.
4. Restore from known-good backups if corruption confirmed.

## 8. Communication Plan

### Internal Updates

- SEV-1: every 30 minutes until stable
- SEV-2: every 60 minutes
- SEV-3: at major milestones

Status update format:

- Incident ID:
- Severity:
- Start time:
- Current impact:
- Actions in progress:
- Next update ETA:

### External/Admin Stakeholder Notice (Template)

Subject: BrightTrack Service Incident Update

Body:

- We are currently investigating a service issue affecting: [feature/users].
- Start time: [timestamp, timezone].
- Current status: [investigating/mitigating/monitoring/resolved].
- Workaround (if any): [details].
- Next update: [time].

## 9. Evidence and Logging Requirements

During incident handling:

- keep an incident action log with timestamps,
- preserve application logs and audit exports,
- do not delete suspicious records,
- record all containment and recovery changes (who/what/when).

Recommended incident artifact folder convention:

`/incident_records/YYYY-MM-DD-INC-<id>/`

Suggested contents:

- `timeline.md`
- `impact_assessment.md`
- `actions_taken.md`
- `postmortem.md`

## 10. Readiness and Drills

Run at least quarterly:

- tabletop scenario (breach, outage, auth failure),
- backup and restore verification,
- audit integrity verification drill,
- incident communication dry run.

Track improvements in a dedicated hardening backlog.

## 11. Incident Closure Criteria

An incident is closed only when:

1. service is stable and monitored,
2. root cause is documented (or bounded with clear follow-up),
3. corrective actions are assigned owners and due dates,
4. stakeholder communication is completed.

## 12. Document Control

- Owner: Engineering / Security Lead
- Review frequency: every 6 months or after any SEV-1/SEV-2
- Last updated: 2026-04-16

