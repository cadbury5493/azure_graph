Unified CIS Compliance Architecture and Workflow
Overview

This document describes the proposed unified architecture for managing CIS baselines, waivers, OS image builds, and compliance scanning across three teams:

GCS (Governance and Compliance Security)

Image Bakery (IB)

Configuration Management (CM)

The goal is to eliminate silos, consolidate baselines and waivers, standardize approval workflows, and automate end-to-end compliance scanning for OS images.

Problem Statement

Today, GCS, Image Bakery, and Configuration Management teams operate independently with separate repositories and processes for:

CIS baselines

Waiver management

Image build logic

Compliance profiles

Automated scanning

This results in the following issues:

Issue	Impact
Multiple teams maintain separate CIS profiles	Duplication and drift
Separate waiver sets	Inconsistent compliance results
Manual GCS validation	Delays and audit challenges
No standardized PR workflow	Uncontrolled changes
No unified CI/CD pipeline	Inefficient validation and releases
Poor audit trails	Difficult to track approvals and changes

A single, unified repository and standardized workflow resolves these gaps.

Proposed Unified Repository Structure
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

Architecture Diagram (Pull Request to Release Workflow)

You may upload the provided PNG diagram.
Place it here under this section in Confluence.

Workflow Summary

The architecture includes two main automated workflows:

Pull Request Workflow (Validation Pipeline)

Release Workflow (Triggered when merging to master)

Both workflows rely on a unified repository and GitHub Code Owners to enforce approvals.

Pull Request Workflow (Validation Pipeline)

This workflow ensures that any proposed change follows compliance, baselines, and waiver governance before being allowed into master.

Steps

Developer raises Pull Request

This PR can include:

Baseline changes

New waivers

InSpec profile updates

Packer or Ansible changes

Image configuration updates

CI Pipeline is automatically triggered

Stages executed:

Linting

Build Image using Packer

Deploy Test VM

Run Qualys Scan

Run InSpec Scan (Configuration Management profiles)

Apply GCS-approved waivers

Compliance evaluation (Passing threshold ≥ 95 percent)

Pipeline produces outcome

If Failed:

PR is blocked

Developer notified

Corrections required

If Passed:

PR becomes eligible for merge

Required approvers defined in CODEOWNERS must approve

GCS team reviews waiver requests (if any submitted)

Waiver changes must be approved exclusively by GCS

Merge to Master Workflow

When a Pull Request is approved and merged into master:

Release pipeline is automatically triggered

The system rebuilds the image from the master branch

Full validation is repeated:

Qualys Scan

InSpec Scan

Waiver application

Compliance calculation

If compliant, the resulting image is promoted to Artifactory as an approved release artifact

Release notes and reports are stored automatically for audit purposes

If the master merge fails the release pipeline:

The pipeline marks the release as failed

The merge remains but the image is not promoted

A corrective PR must be raised

Release Workflow

The following stages occur after merging to master:

Rebuild the OS image based on the authoritative master branch

Provision VM and execute all validation scans

Apply official GCS waivers

Perform compliance evaluation

If compliant (≥ 95 percent), publish artifact to Artifactory

Generate compliance reports and store them in the repository or designated storage area

Code Ownership and Governance

The repository uses CODEOWNERS to enforce strict approval flows.

Path	Owner	Description
gcs/baselines	GCS Team	Only GCS can approve changes
gcs/waivers	GCS Team	All waiver requests require GCS review
config-management/inspec-profiles	CM Team	CM ownership of scanning logic
image-bakery/	IB Team	Only IB can approve image build changes
pipelines/	Platform/DevOps	Shared responsibility

This ensures each team remains accountable for its domain while collaborating within the same repository.

Benefits of the Unified Architecture
Operational Benefits

Elimination of duplicated work across teams

Centralized baselines and waivers

Improved collaboration

Standardized workflows for all OS flavors

Compliance Benefits

Single source of truth for governance

Complete audit trail for baselines, waivers, and changes

Consistent validation using Qualys and InSpec

Engineering Benefits

Automated image validation and release pipeline

Reproducible and reliable images

Gated PRs ensure quality before merging

Next Steps

Create the unified GitHub repository

Implement folder structure

Add CODEOWNERS file

Implement CI/CD workflows

Migrate existing profiles, baselines, waivers, and packer templates

Standardize waiver formats across teams

Perform initial pilot testing

Fully onboard all teams into shared workflow

If you want, I can also provide:

CODEOWNERS file

Waiver JSON/YAML schema

Example pull request templates

Complete pipeline YAML (GitHub Actions or Azure DevOps)

Just let me know.
