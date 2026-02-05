# Agentic Honey-Pot for Scam Detection & Intelligence Extraction
## Overview

Agentic Honey-Pot is a lightweight FastAPI service designed for scam detection, autonomous engagement, and intelligence extraction.
It simulates a responsive victim persona that detects scam intent, adapts its behavior across conversation phases, and harvests actionable scammer intelligence over multiple turns.

The system is built to operate as a webhook-driven service that can be embedded into messaging platforms, moderation pipelines, or fraud-analysis workflows.

## Core Capabilities
### 1. Scam Detection

Identifies scam intent from incoming conversation events

Uses a hybrid approach:

Heuristic signals (keywords, urgency, currency patterns, links, long numeric strings)

Optional LLM-based classification

Produces a confidence score and interpretable signals

### 2. Autonomous Engagement

Once scam intent is detected, the system switches into an agentic persona that engages the scammer intentionally.

The agent operates as a phase-aware state machine:

HOOK – signals compliance and interest

PROBE – asks clarification questions to elicit sensitive details

HARVEST – maximizes extraction of financial and infrastructural data

Engagement continues across turns while maintaining conversation context.

### 3. Intelligence Extraction

During engagement, the service extracts and normalizes actionable artifacts using a regex-first pipeline, including:

Bank account numbers + IFSC codes

UPI IDs

Phishing URLs

Monetary amounts

Each extracted item is returned with an associated confidence score.

### 4. Structured Output

Every webhook response returns a machine-readable JSON payload containing:

Scam detection result and confidence

Current engagement phase

Generated agent reply

Extracted intelligence artifacts

Conversation engagement metadata

Detection signals and reasoning summary

This makes the service suitable for:

Fraud dashboards

Automated reporting pipelines

Downstream enrichment or blacklisting systems

## API Interface
Endpoint

POST /webhook

## Purpose

Processes the latest scammer message, updates conversation state, decides whether to engage, and returns detection + intelligence results.

## Request Fields

conversation_id – Unique identifier per scammer thread

message_id – Optional idempotency key

message – Latest scammer message

history – Optional prior turns (user / agent)

metadata – Reserved for future use (source, locale, channel)

## Response Structure

The response includes:

Detection

scam_detected

confidence

signals

reasoning

Engagement

Current phase

Generated reply

Turn count and last messages

Extracted Intelligence

Bank accounts

UPI IDs

URLs

Amounts
(each with confidence scores)

## Conversation State Management

Each conversation is tracked independently with:

Full turn history

Current engagement phase

Deduplicated extracted artifacts

TTL-based cleanup

Message-level idempotency

This enables long-running scam engagements without cross-thread contamination.

## Architecture Overview
### Key Components

API Layer

Request validation

API-key authentication

Response serialization

Detector

Heuristic scoring engine

Optional LLM classification

Outputs detection confidence, phase hints, and signals

Agent

Autonomous persona controller

Phase-based engagement logic (HOOK → PROBE → HARVEST)

LLM-driven or deterministic fallback responses

Extraction Engine

Regex-first artifact detection

Light normalization (IFSC casing, URL cleanup, currency formatting)

State Store

In-memory conversation tracking

TTL cleanup and deduplication

## Design Goals

Minimal, fast, and webhook-friendly.

Safe, controlled scammer engagement

High signal-to-noise intelligence extraction

LLM-optional (works with or without model access)

Easy integration into existing fraud pipelines
