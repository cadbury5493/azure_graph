Unified CIS Compliance Governance – Architecture and Workflow

This document describes the unified architecture, workflow, and repository organization for streamlining CIS compliance across the GCS, Image Bakery, and Configuration Management teams. It defines how pull requests initiate automated pipelines, how merges to the main branch trigger release workflows, and how artifacts are validated and promoted.

1. Overview

Three teams contribute to CIS compliance:

The GCS team maintains CIS baselines, waiver policies, and approves waiver requests.

The Image Bakery team builds OS base images using Packer and Ansible.

The Configuration Management team develops InSpec profiles and performs compliance scanning.

Currently these teams work independently, resulting in duplication of baselines, profiles, and waivers. The workflow is largely manual, lacks auditability, and does not provide a single source of truth.

The goal of this architecture is to unify all work into a single GitHub repository with automated pipelines for validation, scanning, and release.

2. Proposed Unified Repository Structure
root/
│
├── gcs/
│   ├── baselines/
│   ├── waivers/
│   └── policies/
│
├── image-bakery/
│   ├── packer/
│   ├── ansible/
│   └── scripts/
│
├── config-management/
│   ├── inspec-profiles/
│   ├── scan-engine/
│   └── utilities/
│
├── pipelines/
│   ├── ci-cd/
│   └── scripts/
│
└── CODEOWNERS


This structure ensures:

GCS owns baselines and waivers.

Image Bakery owns Packer templates and build logic.

Configuration Management owns InSpec profiles and scanning utilities.

Pipelines are centralized and shared.

3. Pull Request Workflow

Whenever a developer or team raises a pull request, the following automated workflow begins:

CI pipeline is triggered.

Linting is executed to validate formatting and structure.

A temporary image is built using Packer.

A test VM is deployed using the built image.

Qualys scan runs against the VM.

InSpec scan runs using Configuration Management profiles.

GCS waivers are applied automatically.

Compliance score is calculated.

Compliance threshold: 95 percent or above.

If compliance passes:

The pull request becomes eligible for merge.

Mandatory reviewers (enforced using CODEOWNERS) must approve the change.

If compliance fails:

The pull request is blocked.

A detailed compliance report is generated for remediation.

This ensures that no change enters the main branch unless it passes all compliance gates.

4. Merge to Main Branch Workflow

When a pull request is merged into the main branch:

The release pipeline is triggered automatically.

The image is rebuilt from the main branch to guarantee reproducibility.

All validation scans are rerun:

Qualys compliance

InSpec profile validation

Waiver enforcement

The final compliance score is recalculated.

If compliant, the image is eligible for promotion.

5. Release Workflow

Once the release pipeline completes validation:

The image is versioned and promoted to Artifactory.

Release artifacts and compliance reports are archived for audit purposes.

Release notes are generated automatically.

Version tagging is applied to the repository.

Only fully validated, compliant images are stored in Artifactory.

6. Architecture Diagram

The architectural workflow diagram visually represents the PR pipeline, merge pipeline, and release pipeline.

(The PNG you downloaded can be uploaded here.)

Recommended placement in Confluence:

Insert the diagram directly under this section.

7. Governance and Code Ownership

A CODEOWNERS file enforces approval rules:

GCS must approve changes to baselines and waivers.

Configuration Management must approve changes to InSpec profiles.

Image Bakery must approve changes to Packer templates and build scripts.

Pipeline modifications require Platform or DevOps approval.

This guarantees traceable reviews and proper governance.

8. Benefits of the Unified Architecture

This architecture provides the following benefits:

Operational

Eliminates duplication of baselines, waivers, and profiles.

Creates a single source of truth across all teams.

Compliance

Ensures uniform enforcement of CIS benchmarks.

Provides complete audit trails for all changes.

Engineering

Standardizes build and release processes.

Automates all validation and scanning steps.

Cross-team Collaboration

Centralizes changes in a unified repository.

Enables structured review and approval workflows.

9. Next Steps

Create the unified GitHub repository.

Apply the folder structure described above.

Implement CODEOWNERS with required approvals.

Build and integrate the CI and release pipelines.

Migrate GCS baselines, waivers, and InSpec profiles.

Migrate Image Bakery templates.

Validate the end-to-end workflow.

Begin using the unified pipeline for all OS flavor releases.

If you want this rewritten in a more formal style, a lightweight version, or formatted with Confluence macros such as panels, tables, or expand sections, it can be provided.
