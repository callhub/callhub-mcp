# CallHub Agent Activation Guide

This comprehensive guide explains how to use the agent activation and automation features in the CallHub MCP.

## Table of Contents
- [Overview](#overview)
- [Agent Creation and Activation Workflow](#agent-creation-and-activation-workflow)
- [Available Tools](#available-tools)
- [Basic Agent Activation](#basic-agent-activation)
- [Batch Activation for Large-Scale Deployments](#batch-activation-for-large-scale-deployments)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The agent activation process in CallHub involves several steps:

1. **Create Teams** - Create teams for organizing agents
2. **Create Agents** - Create pending agents assigned to teams
3. **Export Activation URLs** - Get activation URLs for pending agents
4. **Activate Agents** - Complete the activation process with passwords

This guide explains how to automate these steps using the CallHub MCP tools.

## Agent Creation and Activation Workflow

### 1. Creating Teams

First, create the necessary teams:

```python
# List existing teams
team_list = listTeams(account="default")

# Create a new team
team_result = createTeam(account="default", name="Sales Team")
```

### 2. Creating Agents

Create new agents and assign them to teams:

```python
# Create a single agent
agent_result = createAgent(
    account="default",
    email="agent1@example.com",
    username="salesagent1",
    team="Sales Team"  # Use team name, not ID
)
```

**IMPORTANT**: 
- Newly created agents exist in a 'pending' state 
- They will NOT be visible through the standard listAgents API (even with include_pending=true)
- They are not manageable through direct API calls
- Only email, username, and team fields are supported

### 3. Exporting Activation URLs

Once agents are created, export their activation URLs:

```python
# Get direct URL for manual export
export_url_result = getAgentActivationExportUrl(account="default")

# IMPORTANT: The user must download the CSV file manually from this URL
# Pending agents are NOT accessible through direct API calls
```

### 4. Processing the Activation CSV

After downloading the CSV file, process it:

```python
# If user has uploaded the CSV file to the conversation 
csv_result = processUploadedActivationCsv(file_path="activation_export.csv")

# Or if you have the CSV content as a string
csv_content = "..."  # CSV content as string
csv_result = processAgentActivationCsv(csv_content=csv_content)

# Save activations for the next step
activations = csv_result.get("activation_data", [])
```

### 5. Activating Agents

Activate the agents by setting their passwords:

```python
# Activate all agents with a common password
activation_result = activateAgentsWithPassword(
    activation_data=activations,
    password="SecurePassword123",
    account="default"
)
```

## Available Tools

### Agent Creation and Management

- **createAgent**: Create a new agent with required email, username, and team
  ```
  createAgent(account="default", email="agent@example.com", username="agent1", team="Sales Team")
  ```

- **listAgents**: List existing agents (will not show pending agents)
  ```
  listAgents(account="default", include_pending=True)
  ```

### Activation URL Export

- **getAgentActivationExportUrl**: Get a direct URL for exporting agent activation data manually
  ```
  getAgentActivationExportUrl(account="default")
  ```

- **processUploadedActivationCsv**: Process an uploaded CSV file containing activation URLs
  ```
  processUploadedActivationCsv(file_path="activation_export.csv")
  ```

- **processAgentActivationCsv**: Process CSV content as a string
  ```
  processAgentActivationCsv(csv_content="...")
  ```

### Agent Activation

- **activateAgentsWithPassword**: Activate agents using their activation URLs and a common password
  ```
  activateAgentsWithPassword(activation_data=[...], password="SecurePassword123", account="default")
  ```

- **activateAgentsWithBatchPassword**: Activate agents in batches with progress tracking
  ```
  activateAgentsWithBatchPassword(account="default", password="SecurePass123", activation_data=[...], batch_size=10)
  ```

- **getActivationStatus**: Check the current status of an activation job
  ```
  getActivationStatus(account="default")
  ```

- **resetActivationState**: Reset the progress tracking state for agent activation
  ```
  resetActivationState(account="default")
  ```



## Basic Agent Activation

The basic activation flow follows these steps:

1. Create teams and agents (if needed)
2. Get the activation export URL
3. Download the CSV file manually
4. Process the activation CSV
5. Activate agents with a password

Example:

```python
# Step 1: Get the export URL
export_url_result = getAgentActivationExportUrl(account="default")
print(f"Please download the CSV file from: {export_url_result['url']}")

# Step 2: After user has downloaded and uploaded the CSV
csv_result = processUploadedActivationCsv(file_path="activation_export.csv")
activations = csv_result.get("activation_data", [])

# Step 3: Activate agents
if activations:
    activation_result = activateAgentsWithPassword(
        activation_data=activations,
        password="SecurePassword123",
        account="default"
    )
    
    # Step 4: Check results
    successful = activation_result.get("successful_activations", 0)
    failed = activation_result.get("failed_activations", 0)
    print(f"Activated {successful} out of {len(activations)} agents")
```

## Batch Activation for Large-Scale Deployments

For activating large numbers of agents (dozens or hundreds), use the batch activation tools:

### Key Features

- **Batch Processing**: Activates agents in smaller batches for reliability
- **File-Based Logging**: Writes detailed progress to a log file you can monitor
- **Background Processing**: Continues running even if you close the conversation
- **Resumability**: Can resume from where it left off if interrupted
- **State Tracking**: Maintains state between runs to avoid duplicating work
- **Progress Estimation**: Provides time estimates for completion
- **No Context Window Limitations**: Process any number of agents without context issues

### Batch Activation Process

```python
# Step 1: Get and process the activation CSV
csv_result = processUploadedActivationCsv(file_path="activation_export.csv")
activation_data = csv_result.get("activation_data", [])

# Step 2: Activate in batches with file-based logging
if activation_data:
    batch_result = activateAgentsWithBatchPassword(
        account="default",
        password="SecurePassword123",
        activation_data=activation_data,
        batch_size=20  # You can use larger batch sizes now, since updates go to the log file
    )
    
    # Get the log file path for monitoring
    log_file = batch_result.get("log_file")
    print(f"Activation in progress. Monitor the log file at: {log_file}")
    
# Step 3: Check status and log file location
status = getActivationStatus(account="default")
print(f"Activation progress: {status['completed_count']} of {status['total_count']} agents processed")
print(f"Log file: {status['log_file']}")

# Step 4 (if needed): Resume an interrupted process
if status['in_progress'] or status['completed_count'] < status['total_count']:
    # Re-run with the same parameters to resume (activation will continue from where it left off)
    batch_result = activateAgentsWithBatchPassword(
        account="default",
        password="SecurePassword123",
        activation_data=activation_data,
        batch_size=20
    )

# If you need to restart the process completely:
reset_result = resetActivationState(account="default")
```

## Best Practices

### Agent Creation

1. **Create teams first**: Always create and verify teams before creating agents
2. **Unique usernames**: Ensure agent usernames are unique across your entire CallHub account
3. **Email domains**: Use valid email domains for agent emails (activation emails will be sent)
4. **Team names**: Use team names (strings), not team IDs when creating agents

### Activation Process

1. **Strong passwords**: Use secure passwords (8+ characters)
2. **Optimal batch sizes**: Use batch sizes of 15-30 agents for best performance
3. **Monitor log files**: Check the log file periodically to see progress
4. **Process any number of agents**: No need to split activations - process hundreds at once
5. **Preserve CSV**: Keep your activation CSV files until all agents are fully activated
6. **Resume interrupted processes**: If activation is interrupted, you can resume using the same activation data

### Security

1. **Password management**: Consider using a password manager to generate and store agent passwords
2. **Activation timing**: Complete the activation process shortly after agent creation
3. **Password policy**: Implement a policy for agents to change their initial passwords

## Troubleshooting

### Common Issues

1. **Authentication Failures**: Make sure you're logged into CallHub when manually downloading the activation CSV.

2. **Element Not Found**: If the browser automation fails to find UI elements, it may be due to CallHub UI changes. Check logs.

3. **Rate Limiting**: If activating many agents, you might hit rate limits. The batch activation tools handle this automatically.

4. **Password Requirements**: CallHub requires passwords to be at least 8 characters. The tools validate this.

5. **Missing Activation URLs**: If no activation URLs are found:
   - Verify that agents were created successfully
   - Ensure agents are still in pending state (not already activated)
   - Check that you have permission to manage agents

6. **CSV Format Issues**: If the CSV processing fails:
   - Ensure you're using the CSV file directly from CallHub
   - Do not modify the CSV file structure
   - Check for special characters in agent names or emails

## File-Based Activation Logging

When activating large numbers of agents, the system automatically logs all progress to a file. This is a better approach than trying to stream updates through the conversation with your AI assistant, as it:

1. **Avoids context window limitations** - The log file can be as large as needed
2. **Provides more detailed logs** - Every step of the process is recorded
3. **Continues in the background** - The activation keeps running even if you close the conversation
4. **Allows easy resumption** - If interrupted, you can resume from where you left off

### Log File Location

The activation logs are stored in the `~/callhub_logs/` directory (your home directory) with a name format of:
```
callhub_activation_{account_name}_{date}.log
```

For example: `callhub_activation_default_20250513.log`

### Log File Contents

The log file contains detailed information about each step of the activation process:

```
[2025-05-13 14:30:25] ========================================
[2025-05-13 14:30:25] STARTING AGENT ACTIVATION PROCESS
[2025-05-13 14:30:25] Account: default
[2025-05-13 14:30:25] Agents to process: 100
[2025-05-13 14:30:25] Batch size: 10
[2025-05-13 14:30:25] Log file: /Users/username/callhub_logs/callhub_activation_default_20250513.log
[2025-05-13 14:30:25] ========================================
[2025-05-13 14:30:25] *** BATCH 1/10 STARTED *** Processing 10 agents (100 total)
[2025-05-13 14:30:30] Agent 1/100 'agent1': SUCCESS
[2025-05-13 14:30:35] Agent 2/100 'agent2': SUCCESS
...
[2025-05-13 14:31:15] *** BATCH 1/10 COMPLETE *** Results: 10 successful, 0 failed | Overall progress: 10 successful, 0 failed (10.0%)
...
[2025-05-13 14:45:25] ========================================
[2025-05-13 14:45:25] ACTIVATION PROCESS COMPLETE
[2025-05-13 14:45:25] Total successful: 97
[2025-05-13 14:45:25] Total failed: 3
[2025-05-13 14:45:25] Success rate: 97.0%
[2025-05-13 14:45:25] ========================================
```
