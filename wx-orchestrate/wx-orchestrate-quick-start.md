# Orchestrate Solution

## Overview
This solution provides a complete reference framework for building watsonx Orchestrate applications with multiple integration patterns. It demonstrates how to structure both native and external services through MCP servers, self-hosted APIs, and enterprise system connections.

**Problem it solves:**
- Lack of examples for OAuth2 connections to enterprise systems
- Need for watsonx.ai integration within Orchestrate workflows
- Format to include servicenow and salesforce tools
- How to set up MCP Servers and import them as toolkits

## Orchestrate
Components built and managed within the watsonx Orchestrate platform

### Agents
Three reference agents demonstrate different integration scenarios:

`test_query_agent`: Routes queries to native Python tools for searching CSV-based data (products, bills, employees). Shows how agents analyze user intent and select appropriate search tools based on the request domain.

`test_connections_agent`: Manages OAuth2-authenticated requests to Salesforce and ServiceNow. Demonstrates intelligent routing between enterprise systems and handling of authenticated API calls.

`test_mcp_agent`: Interfaces with external MCP servers for specialized operations (image rotation, random number generation). 

### Tools
Native tools imported directly into Orchestrate via the CLI:

**table_search.py**: Contains `search_product`, `search_bill`, and `search_employee` functions that query CSV files. Called when agents need to retrieve company data without external dependencies.

**salesforce.py**: Contains `get_salesforce_cases`, `get_case_status`, and `get_all_case_information` functions. Called when agents need to retrieve or update Salesforce case records.

**servicenow.py**: Contains `get_ticket_test` function for ServiceNow incident retrieval. Called when agents need to fetch IT ticket information.

**watsonx_ai_call.py**: Contains `recommend_best_product` function that uses watsonx.ai ModelInference to rank and recommend products with AI-generated explanations. Called when agents need AI-enhanced decision making beyond simple data retrieval. Should be used `table_search.search_product`

### Connections
**Salesforce Connection**: Configured OAuth with `salesforce_oauth2_auth_code_ibm_184bdbd3` app ID. Required for all Salesforce tools to access case data via REST API. Uses authorization code flow with automatic token refresh.

**ServiceNow Connection**: Configured OAuth with `servicenow_oauth2_auth_code_ibm_184bdbd3` app ID. Required for ServiceNow ticket retrieval. Uses OAuth2 bearer tokens passed in request headers.

## External
Components hosted outside Orchestrate 

### Platform (Code Engine, Docker, etc.)

**Code Engine (external/code-engine/)**: FastMCP application (`main.py`) containerized with Docker.

**Self-Hosted (external/Self-hosted/)**: Generic external API defined by OpenAPI spec (`open_api_spec.json`). Represents on-premise or third-party services accessed via HTTP. Can run anywhere with network access to Orchestrate.

### Method (MCP, A2A, Requests)

**MCP (Model Context Protocol)**: 
Format is shown at `code-engine/api` and explains how to import it with the CLI.

**OpenAPI Import**: Used for Code Engine and self-hosted APIs. Services expose OpenAPI specs that Orchestrate imports.

### Tools

**MCP Tools (via FastMCP server)**:
- `rotate_image`: Rotates base64-encoded images by specified angles
- `random_number_in_range`: Generates random numbers within specified bounds
- `health_check`: Verifies MCP server connectivity

**Open API Imported Tools**:
- `open_api_spec.json`: Demonstrates generic open api spec


**Self-Hosted Tools (via OpenAPI)**:
- Defined in `open_api_spec.json`
- Generic external service pattern for integration with existing APIs