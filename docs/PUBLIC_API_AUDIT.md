# CallHub MCP Server — Public API Audit

**Audit date:** 2026-05-23  
**Source:** https://developer.callhub.io/reference  
**MCP server:** `src/server.py`  
**Constants file:** `src/callhub/constants.py`

---

## Methodology

1. Every public endpoint listed in `developer.callhub.io` was fetched and catalogued.
2. Every `@server.tool` registration in `server.py` was extracted and matched against the endpoint it calls (via the module implementations).
3. Gaps, mismatches, and non-public usage were identified.

---

## A. Missing from MCP (in public API but no MCP tool)

### A1 — Endpoint: DELETE /v1/callcenter_campaigns/:id/
- **Method:** DELETE  
- **Path:** `https://api.callhub.io/v1/callcenter_campaigns/{id}/`  
- **What it does:** Permanently deletes a call center (power) campaign.  
- **Priority: P1** — The MCP has `updateCallCenterCampaign` and `createCallCenterCampaign` but no delete.

### A2 — Endpoint: DELETE /v1/voice_broadcasts/:id/
- **Method:** DELETE  
- **Path:** `https://api.callhub.io/v1/voice_broadcasts/{id}/`  
- **What it does:** Permanently deletes a voice broadcast campaign.  
- **Priority: P1** — CRUD is incomplete without delete.

### A3 — Endpoint: DELETE /v1/sms_campaigns/:id/
- **Method:** DELETE  
- **Path:** `https://api.callhub.io/v1/sms_campaigns/{id}/`  
- **What it does:** Permanently deletes an SMS campaign.  
- **Priority: P1** — CRUD is incomplete without delete.

### A4 — Endpoint: PUT /v1/voice_broadcasts/:id/
- **Method:** PUT  
- **Path:** `https://api.callhub.io/v1/voice_broadcasts/{id}/`  
- **Parameters:** `name` (string), `status` (int32), `frequency` (int32, calls per minute)  
- **What it does:** Updates name, status, or call frequency of an existing VB campaign.  
- **Priority: P1** — The MCP has `listVoiceBroadcastCampaigns`, `createVbCampaign`, and `duplicateVbCampaign`, but no update/status-change tool.

### A5 — Endpoint: POST /v1/media/upload/
- **Method:** POST  
- **Path:** `https://api.callhub.io/v1/media/upload/`  
- **Parameters:** `file` (binary, required), `name` (string, optional), `generate_gif` (string, optional)  
- **Returns:** `media_file_id` or `job_id` for async video processing  
- **What it does:** Uploads audio/video/image files to the media library for use in campaigns.  
- **Priority: P1** — VB and SMS campaigns reference media. Without upload, users must manage media outside MCP.

### A6 — Endpoint: POST /suppression-lists/:id/contacts/
- **Method:** POST  
- **Path:** `https://api.callhub.io/suppression-lists/{id}/contacts/`  
- **Parameters:** `id` (path, int32), body: array of `{phone_number, mobile}` objects  
- **Returns:** 207 Multi-Status  
- **What it does:** Adds contacts to a suppression list (similar to DNC but at suppression-list level).  
- **Priority: P2** — Distinct from DNC lists; useful for campaign-scoped suppression.

### A7 — Endpoint: POST /enterprise-account/share-credits/
- **Method:** POST  
- **Path:** `https://api.callhub.io/enterprise-account/share-credits/`  
- **Parameters:** `subaccount` (string), `transfer_amount` (int32)  
- **What it does:** Transfers credits from the main account to a subaccount.  
- **Priority: P2** — High value for enterprise/multi-account setups.

### A8 — Endpoint: GET /v1/export_data/export_{job_id}/
- **Method:** GET  
- **Path:** `https://api.callhub.io/v1/export_data/export_{job_id}/`  
- **Parameter:** `job_id` (path, string)  
- **What it does:** Retrieves the result of a previously initiated export job (e.g., power campaign export).  
- **Priority: P2** — Required to retrieve results from `exportPowerCampaign` which creates a job but returns a `job_id`. Without this endpoint, exports cannot be completed end-to-end.

### A9 — Endpoint: POST /v2/agent-key/
- **Method:** POST  
- **Path:** `https://api.callhub.io/v2/agent-key/`  
- **Parameters:** `username` (string), `password` (string)  
- **What it does:** Retrieves an authentication token for an agent (agent login).  
- **Priority: P2** — Needed for agent-facing workflows; different from manager API key auth.

### A10 — Endpoint: GET /v2/agent-status/
- **Method:** GET  
- **Path:** `https://api.callhub.io/v2/agent-status/`  
- **What it does:** Gets the current status of an agent (connected, idle, etc.).  
- **Priority: P2** — Useful for monitoring agent availability.

### A11 — Endpoint: GET /v2/user-details/
- **Method:** GET  
- **Path:** `https://api.callhub.io/v2/user-details/`  
- **What it does:** Returns profile details of the currently authenticated agent/user.  
- **Priority: P2** — "Who am I" endpoint; useful for validating credentials and surfacing account info.

### A12 — Endpoint: GET /v2/collective_texting/campaigns/ (agent-facing)
- **Method:** GET  
- **Path:** `https://api.callhub.io/v2/collective_texting/campaigns/`  
- **What it does:** Returns the list of collective texting (P2P) campaigns assigned to the authenticated agent. Distinct from the manager-side `/v1/p2p_campaigns/`.  
- **Priority: P2** — Agent-facing view differs from manager list.

### A13 — Endpoint: GET /v2/collective_texting/campaigns/:campaign_id/questions/
- **Method:** GET  
- **Path:** `https://api.callhub.io/v2/collective_texting/campaigns/{campaign_id}/questions/`  
- **Parameter:** `campaign_id` (path, string)  
- **What it does:** Returns all survey questions for a specific collective texting campaign.  
- **Priority: P2** — The MCP has `getP2pSurveys` (which hits the Snowflake survey-list endpoint) but no dedicated question-listing tool aligned with the public docs path.

### A14 — Endpoint: GET /v2/collective_texting/campaigns/:campaign_id/saved_replies/
- **Method:** GET  
- **Path:** `https://api.callhub.io/v2/collective_texting/campaigns/{campaign_id}/saved_replies/`  
- **Parameter:** `campaign_id` (path, string)  
- **What it does:** Returns saved replies (manager-configured canned responses) for a collective texting campaign.  
- **Priority: P2** — No coverage in MCP at all.

### A15 — Endpoint: GET /v1/p2p_campaigns/api-schema
- **Method:** GET  
- **Path:** `https://api.callhub.io/v1/p2p_campaigns/api-schema`  
- **What it does:** Returns the full JSON schema for creating P2P campaigns.  
- **Priority: P3** — Developer utility; useful for discovery but not day-to-day use.

### A16 — Endpoint: GET /v1/templatesapi-schema
- **Method:** GET  
- **Path:** `https://api.callhub.io/v1/templates/api-schema`  
- **What it does:** Returns the JSON schema for template creation.  
- **Priority: P3** — Developer utility.

### A17 — Endpoint: GET /v1/integration_fields/api-schema
- **Method:** GET  
- **Path:** `https://api.callhub.io/v1/integration_fields/api-schema`  
- **What it does:** Returns the schema for integration fields.  
- **Priority: P3** — Developer utility.

---

## B. Non-public in MCP (MCP tool uses endpoint NOT in developer.callhub.io)

These tools call internal/undocumented endpoints. They may work but are not covered by the public API contract and could break without notice.

| Tool Name | Endpoint Used | Notes | Recommendation |
|-----------|--------------|-------|----------------|
| `updateCallCenterCampaign` | `PATCH /v1/callcenter_campaigns/{id}/` | Public docs specify PUT; MCP uses PATCH. The endpoint itself (`/v1/callcenter_campaigns/{id}/`) is public — only the method is deviant. | Fix method (see Section C). |
| `createCallCenterCampaign` | `POST /v1/power_campaign/create/` | `/v1/power_campaign/` is not listed in developer docs. The public API for listing call center campaigns is `/v1/callcenter_campaigns/`. The internal `power_campaign` path is implementation-only. | Mark as **extended API**; keep as working but undocumented. |
| `duplicatePowerCampaign` | `POST /v1/power_campaign/duplicate/` | Same as above — `/v1/power_campaign/` is not documented publicly. | Mark as **extended API**. |
| `addAgentsToPowerCampaign` | `POST /v1/power_campaign/{id}/agents/add/` | Not in public docs. | Mark as **extended API**. |
| `exportPowerCampaign` | `GET /v1/power_campaign/{id}/export/` | Not in public docs. Related public doc endpoint is `GET /v1/export_data/export_{job_id}/` for polling results. | Mark as **extended API**; add tool for `GET /v1/export_data/export_{job_id}/` to complete the workflow (see A8). |
| `exportCampaignData` | `GET /v1/campaigns/{id}/export` | `/v1/campaigns/` is not in the public API reference; distinct from `/v1/callcenter_campaigns/`. | Mark as **extended API**; verify if actually needed. |
| `getCampaignStatsAdvanced` | `GET /v1/campaigns/{id}/stats` | Same as above — `/v1/campaigns/` not public. | Mark as **extended API**. |
| `getMediaFiles` | `GET /v2/media/` | Public docs only document `POST /v1/media/upload/`. The GET listing is internal. | Mark as **extended API**; keep (useful for discovering media IDs). |
| `getLiveAgents` | `GET /v2/campaign/agent/live/` | Not in public API docs. | Mark as **extended API**; keep (high operational value). |
| `getSmsBroadcast` | `GET /v2/sms_broadcast/{id}/` | Public docs document `POST /v2/sms_broadcast/create/` and `POST /v2/sms_broadcast/{id}/duplicate/`. A GET for a single broadcast is not documented. | Mark as **extended API**. |
| `updateSmsBroadcast` | `PATCH /v2/sms_broadcast/{id}/` | Not in public docs. | Mark as **extended API**. |
| `duplicateSmsBroadcast` | `POST /v2/sms_broadcast/{id}/duplicate/` | **This IS documented publicly** — `POST /v2/sms_broadcast/duplicate/` per docs. However, the MCP puts campaign_id in the path (`/{id}/duplicate/`) while docs show it as a body param at `/duplicate/`. | Fix path (see Section C). |
| `updateP2pCampaign` | `PUT /v2/sms_campaign/snowflake/{id}/` | Uses internal Snowflake path. Public docs reference `/v1/p2p_campaigns/`. | Mark as **extended API**; functions correctly. |
| `createRelationalCampaign` | `POST /email/v1/relational-campaign/create` | Public doc URL is `POST /email/v_1/relational-campaign/create/` — note underscore in `v_1`. The `RELATIONAL_CAMPAIGN` constant is set to `/email/v1/relational-campaign/` which may cause 404. | Fix URL (see Section C). |
| `updateRelationalCampaign` | `PUT /email/v1/relational-campaign/{id}/` | Same URL concern as above. Public docs use `/email/v_1/relational-campaign/{id}/edit`. | Fix URL and path suffix (see Section C). |
| `getRelationalCampaign` | `GET /email/v1/relational-campaign/{id}/` | Same URL concern. Public docs: `/email/v_1/relational-campaign/{campaign_id}/`. | Fix URL (see Section C). |
| `updateRelationalCampaignStatus` | `POST /email/v1/relational-campaign/{id}/update-status/` | Not in public docs. | Mark as **extended API**. |
| `duplicateRelationalCampaign` | `POST /email/v1/relational-campaign/{id}/duplicate/` | Not in public docs. | Mark as **extended API**. |
| `assignAgentsToRelationalCampaign` | `PUT /email/v1/relational-campaign/{id}/agents/` | Not in public docs. | Mark as **extended API**. |
| `getAreaCodes` | `GET /v2/get_area_code/` | Not in public docs. | Mark as **extended API**. |
| `getNumberRentRates` | `GET /v1/number_rent_rates/` | Not in public docs. | Mark as **extended API**. |
| `getAutoUnrentSettings` | `GET /v2/auto_unrent/settings/` | Not in public docs. | Mark as **extended API**. |
| `updateAutoUnrentSettings` | `PUT/PATCH /v2/auto_unrent/settings/` | Not in public docs. | Mark as **extended API**. |
| `revalidateNumbers` | `POST /v1/revalidate_numbers/` | Not in public docs. | Mark as **extended API**. |
| `listSmsOnlyNumbers` | `GET /v2/sms_number/show_rented_number/` | Not in public docs. | Mark as **extended API**. |
| `listCombinedSmsNumbers` | `GET /v2/validated_and_rented_numbers/` | Not in public docs. | Mark as **extended API**. |
| `autoRentSmsNumber` | `POST /v2/sms_number/sms_rent_number/` | Not in public docs (public doc is `POST /v1/numbers/rent/`). | Mark as **extended API**. |
| `exportSmsReport` | `GET /v1/sms_campaign/sms_report/export/` | Not in public docs. | Mark as **extended API**. |
| `getShortenedUrl` | `GET /v2/shortened-urls/{shortCode}` | Not in public docs. | Mark as **extended API**. |
| `listShortenedUrls` | `GET /v2/shortened-urls/` | Not in public docs. | Mark as **extended API**. |
| `getApiSchema` | Internal schema fetch | Not a CallHub API call — reads internal schema files. | Keep as utility. |
| Agent activation tools (5 tools) | Browser automation via Selenium | Not API calls at all — browser automation against the UI. | Keep for activation workflow but document clearly as UI automation, not API. |

---

## C. Incorrectly Implemented (wrong method, wrong params, wrong URL)

### C1 — `updateCallCenterCampaign`: PATCH vs PUT
- **Tool:** `updateCallCenterCampaign` in `campaigns.py` line 87  
- **MCP uses:** `PATCH /v1/callcenter_campaigns/{id}/`  
- **Public docs say:** `PUT /v1/callcenter_campaigns/{id}/` with `name` (string) and `status` (int32) body parameters  
- **Impact:** PATCH may work on some DRF backends but is non-standard vs. the documented contract. The tool also only sends `status`, never `name`.  
- **Fix:** Change method to `PUT`; add optional `name` parameter.

### C2 — `createWebhook`: wrong field names in validation vs. implementation
- **Tool:** `createWebhook` in `server.py` (tool takes `event_name`, `target_url`) and `webhooks.py` (implementation accepts `event_name` OR `event`, `target_url` OR `target`)  
- **Public docs say:** body fields are `event` (string) and `target` (string)  
- **Impact:** The tool-level parameter names (`event_name`, `target_url`) differ from the API contract names (`event`, `target`). The implementation correctly maps them internally, so this works — but the tool description says "Valid event types: 'vb.transfer'..." while the public docs don't restrict to those 4 values (the full event list may be broader). The hardcoded validation against only 4 event types may reject valid events.  
- **Fix:** Update tool param names to match API (`event`, `target`) or at minimum clarify in description. Re-examine the allowed event types list.

### C3 — `duplicateSmsBroadcast`: wrong endpoint path
- **Tool:** `duplicate_sms_broadcast` in `sms_broadcasts.py` line 187  
- **MCP uses:** `POST /v2/sms_broadcast/{campaign_id}/duplicate/`  
- **Public docs say:** `POST /v2/sms_broadcast/duplicate/` with `campaign_id` as a body/path parameter  
- **Impact:** The MCP puts `campaign_id` in the URL path; the public docs show it differently. If the server doesn't accept the path-parameterized form, this will 404.  
- **Fix:** Verify actual server behavior; if needed, align with documented form.

### C4 — Relational campaign URL: `v1` vs `v_1`
- **Tools:** `createRelationalCampaign`, `updateRelationalCampaign`, `getRelationalCampaign`, `updateRelationalCampaignStatus`, `duplicateRelationalCampaign`, `assignAgentsToRelationalCampaign`  
- **MCP constant:** `RELATIONAL_CAMPAIGN = "/email/v1/relational-campaign/"` (in `constants.py`)  
- **Public docs say:** `POST /email/v_1/relational-campaign/create/` — uses `v_1` (with underscore), not `v1`  
- **Impact:** All relational campaign tools will hit `/email/v1/...` while the actual endpoint is `/email/v_1/...`. This is a likely 404 or routing mismatch.  
- **Fix:** Change constant to `"/email/v_1/relational-campaign/"`.

### C5 — `updateRelationalCampaign`: path suffix mismatch
- **Tool:** `update_relational_organizing_campaign` in `relational_organizing.py` line 49  
- **MCP uses:** `PUT /email/v1/relational-campaign/{id}/` (no edit suffix)  
- **Public docs say:** `PUT /email/v_1/relational-campaign/{campaign_id}/edit`  
- **Impact:** Beyond the `v_1` issue (C4), the update path is missing `/edit` suffix.  
- **Fix:** Change endpoint to `f"{ENDPOINTS.RELATIONAL_CAMPAIGN}{campaign_id}/edit"`.

### C6 — `rentNumber`: MCP sends `campaign_type` but public docs don't mention it as a user param
- **Tool:** `rent_number_tool` in `server.py`  
- **Public docs say:** `country_iso` (required), `phone_number_prefix` (optional), `campaign_type` (optional: `CALL_CENTER` or `VOICE_BROADCAST`)  
- **MCP implementation:** Does not pass `campaign_type` to the API at all despite accepting it as a param  
- **Minor issue:** The parameter is accepted in the tool signature but silently dropped in `numbers.py`. No functional breakage but the feature is documented and could be useful.  
- **Fix:** Pass `campaign_type` to the API call in `numbers.py`.

### C7 — `getCreditUsage` uses POST but tool description implies GET semantics
- **Tool:** `getCreditUsage` / `get_credit_usage` in `users.py` line 66  
- **Public docs confirm:** `POST /v2/credits_usage/` with body params — this is correct behavior  
- **Issue:** The tool description says "Retrieve credit usage details" (read-like) but the implementation is correctly POST. No code fix needed — this is just a description accuracy note.  
- **Verdict:** Correctly implemented; description could be clarified.

### C8 — `listRentedNumbers`: missing query parameters
- **Tool:** `listRentedNumbers` / `list_rented_numbers` in `numbers.py`  
- **MCP sends:** bare GET with no query params  
- **Public docs document:** `page_size`, `page`, `countries`, `regions`, `phone_number_prefix`, `order_by`, `order_direction`, `include_running_campaign_numbers`  
- **Impact:** The tool always returns the first page with no filtering. For accounts with many numbers, this is a usability gap.  
- **Fix:** Expose at least `page`, `page_size`, and `countries` as tool parameters.

### C9 — `listValidatedNumbers`: missing query parameters
- **Tool:** `listValidatedNumbers` / `list_validated_numbers` in `numbers.py`  
- **MCP sends:** bare GET with no query params  
- **Public docs document:** `page_size`, `page` for pagination  
- **Fix:** Expose `page` and `page_size`.

---

## D. Implementation Recommendations

### Tier 1 — Critical bugs to fix immediately (correctness issues)

1. **Fix relational campaign URL** (`/email/v1/` → `/email/v_1/`) in `constants.py` and add `/edit` suffix to the update path in `relational_organizing.py`. All 6 relational campaign tools are broken without this fix.

2. **Fix `updateCallCenterCampaign` HTTP method** from PATCH to PUT and accept optional `name` parameter. Aligns with public contract.

3. **Fix `updateRelationalCampaign` path** to include `/edit` suffix (part of Tier 1 bundle with the URL fix).

### Tier 2 — High-value missing tools (P1 missing endpoints)

4. **Add `deleteCallCenterCampaign`** — `DELETE /v1/callcenter_campaigns/{id}/`. One-liner tool.

5. **Add `deleteVoiceBroadcastCampaign`** — `DELETE /v1/voice_broadcasts/{id}/`. One-liner tool.

6. **Add `deleteSmsCampaign`** — `DELETE /v1/sms_campaigns/{id}/`. One-liner tool.

7. **Add `updateVoiceBroadcastCampaign`** — `PUT /v1/voice_broadcasts/{id}/` with `name`, `status`, `frequency`. Completes VB CRUD.

8. **Add `uploadMediaFile`** — `POST /v1/media/upload/` with `file` (binary), `name`, `generate_gif`. Required for VB campaign creation from scratch.

### Tier 3 — Medium-value additions (P2 missing endpoints)

9. **Add `getExportJobResult`** — `GET /v1/export_data/export_{job_id}/`. Completes the power campaign export workflow (currently `exportPowerCampaign` returns a job_id with no way to retrieve the result).

10. **Add `shareCredits`** — `POST /enterprise-account/share-credits/` with `subaccount`, `transfer_amount`. High value for enterprise accounts.

11. **Add `getAgentKey`** — `POST /v2/agent-key/` with `username`, `password`. Enables agent-credential workflows.

12. **Add `getAgentStatus`** — `GET /v2/agent-status/`. Useful for monitoring.

13. **Add `getUserDetails`** — `GET /v2/user-details/`. "Who am I" endpoint.

14. **Add `addContactsToSuppressionList`** — `POST /suppression-lists/{id}/contacts/`.

15. **Add `getCollectiveTextingQuestions`** — `GET /v2/collective_texting/campaigns/{id}/questions/`. More precise path than existing `getP2pSurveys`.

16. **Add `getCollectiveTextingSavedReplies`** — `GET /v2/collective_texting/campaigns/{id}/saved_replies/`.

17. **Fix `listRentedNumbers`** — expose `page`, `page_size`, `countries`, `order_by` query params.

18. **Fix `listValidatedNumbers`** — expose `page`, `page_size` query params.

### Tier 4 — Polish and consistency

19. **Fix `duplicateSmsBroadcast` path** — verify whether server accepts path-parameterized form; align with docs if not.

20. **Fix `rentNumber`** — actually pass the accepted `campaign_type` parameter to the API.

21. **Fix `createWebhook` event validation** — verify the full allowed event type list and update hardcoded whitelist.

22. **Add schema endpoints** (P3) — `GET /v1/p2p_campaigns/api-schema`, `GET /v1/templates/api-schema`, `GET /v1/integration_fields/api-schema`. Low effort; useful for LLM-based introspection.

---

## Summary Table

| Category | Count |
|----------|-------|
| Missing P1 endpoints (high value, in public docs) | 5 |
| Missing P2 endpoints (medium value, in public docs) | 9 |
| Missing P3 endpoints (utility, in public docs) | 3 |
| Non-public/extended API tools (undocumented but functional) | 28 |
| Incorrectly implemented (wrong method/URL/params) | 6 |
| Total MCP tools registered | ~120 |
| Total public API endpoints documented | ~47 distinct operations |
| MCP coverage of public endpoints | ~35/47 (~75%) |

---

## Appendix: Full MCP Tool Inventory

All `@server.tool` registrations extracted from `server.py`:

**Account management (local, not API):**
`listAccounts`, `configureAccount`, `deleteAccount`

**Agents:**
`fetchAgents`, `listAgents`, `getAgent`, `createAgent`, `getLiveAgents`

**Contacts:**
`listContacts`, `getContact`, `createContact`, `createContactsBulk`, `updateContact`, `deleteContact`, `getContactFields`

**Phonebooks:**
`listPhonebooks`, `getPhonebook`, `createPhonebook`, `updatePhonebook`, `deletePhonebook`, `addContactsToPhonebook`, `removeContactFromPhonebook`, `getPhonebookCount`, `getPhonebookContacts`

**Tags:**
`listTags`, `getTag`, `createTag`, `updateTag`, `deleteTag`, `addTagToContact`, `removeTagFromContact`

**Custom Fields:**
`listCustomFields`, `getCustomField`, `createCustomField`, `updateCustomField`, `deleteCustomField`, `updateContactCustomField`

**Webhooks:**
`listWebhooks`, `getWebhook`, `createWebhook`, `deleteWebhook`

**Call Center / Power Campaigns:**
`listCallCenterCampaigns`, `updateCallCenterCampaign`, `createCallCenterCampaign`, `duplicatePowerCampaign`, `exportCampaignData`, `getCampaignStatsAdvanced`, `addAgentsToPowerCampaign`, `exportPowerCampaign`

**Media:**
`getMediaFiles`

**Phone Numbers:**
`listRentedNumbers`, `listValidatedNumbers`, `rentNumber`, `getAreaCodes`, `getNumberRentRates`, `getAutoUnrentSettings`, `updateAutoUnrentSettings`, `revalidateNumbers`, `listSmsOnlyNumbers`, `listCombinedSmsNumbers`, `autoRentSmsNumber`

**Voice Broadcast:**
`listVoiceBroadcastCampaigns`, `getVbCampaign`, `createVbCampaign`, `createVbCampaignTemplate`, `duplicateVbCampaign`

**SMS Campaigns:**
`listSmsCampaigns`, `updateSmsCampaign`

**SMS Broadcasts:**
`createSmsBroadcast`, `getSmsBroadcast`, `updateSmsBroadcast`, `duplicateSmsBroadcast`

**P2P Campaigns:**
`listP2pCampaigns`, `updateP2pCampaign`, `createP2PCampaign`, `duplicateP2pCampaign`, `getP2pCampaignAgents`, `addAgentsToP2pCampaign`, `reassignP2pAgents`, `getP2pSurveys`

**Users / Credits:**
`getUsers`, `getCreditUsage`

**DNC:**
`createDncContact`, `listDncContacts`, `updateDncContact`, `deleteDncContact`, `createDncList`, `listDncLists`, `updateDncList`, `deleteDncList`

**Teams:**
`listTeams`, `getTeam`, `createTeam`, `updateTeam`, `deleteTeam`, `getTeamAgents`, `getTeamAgentDetails`, `addAgentsToTeam`, `removeAgentsFromTeam`

**Relational Organizing:**
`createRelationalCampaign`, `duplicateRelationalCampaign`, `assignAgentsToRelationalCampaign`, `updateRelationalCampaign`, `getRelationalCampaign`, `updateRelationalCampaignStatus`

**Survey Templates / Questions / Integration Fields:**
`listSurveyTemplates`, `getSurveyTemplate`, `createSurveyTemplate`, `updateSurveyTemplate`, `deleteSurveyTemplate`, `listQuestions`, `getQuestion`, `listIntegrationFields`, `getIntegrationField`

**URLs:**
`getShortenedUrl`, `listShortenedUrls`

**Agent Activation (browser automation):**
`exportAgentActivationUrls`, `getAgentActivationExportUrl`, `processAgentActivationCsv`, `activateAgentsWithPassword`, `processLocalActivationCsv`, `processUploadedActivationCsv`, `processUploadedCsv`, `prepareAgentActivation`, `activateAgentsWithBatchPassword`, `getActivationStatus`, `resetActivationState`

**Utilities:**
`getApiSchema`
