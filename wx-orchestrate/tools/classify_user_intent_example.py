# pre_invoke_classify.py
import os
import json
import time
import base64
import requests

from ibm_watsonx_orchestrate.agent_builder.tools import tool
from ibm_watsonx_orchestrate.agent_builder.tools.types import (
    PythonToolKind,
    PluginContext,
    AgentPreInvokePayload,
    AgentPreInvokeResult,
    Message,
    TextContent,
)
from ibm_watsonx_orchestrate.run import connections
from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType


_local = False

# ----------------------------------------------------------------------
# Helper functions – IAM token handling
# ----------------------------------------------------------------------
def _get_iam_token(iam_api_key: str, iam_url: str) -> str:
    """
    Exchange an IBM Cloud API key for an IAM access token.
    The token is cached in the process for its lifetime (default 1 h).

    Returns:
        str: Bearer token ready for use with Watson x AI.
    """
    # Simple in‑process cache
    cache = getattr(_get_iam_token, "_cache", {})
    token = cache.get("token")
    expiry = cache.get("expiry", 0)

    if token and time.time() < expiry - 60:          # reuse if still valid
        return token

    payload = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": iam_api_key,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(iam_url, data=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    token = data["access_token"]
    # token lifetime is usually 3600 s
    expiry = time.time() + int(data.get("expires_in", 3600))

    # store back into the function attribute
    _get_iam_token._cache = {"token": token, "expiry": expiry}
    return token


def _classify_text(
    text: str,
    *,
    model_id: str,
    project_id: str | None,
    endpoint: str,
    iam_token: str,
) -> str:
    """
    Call the Watson x AI chat endpoint with a short system prompt that forces a
    single‑word classification.

    Returns:
        str: One of ``room_booking``, ``hotel_info`` or ``surroundings``.
    """
    # Minimal prompt that asks the model to output only the label
    system_prompt = (
        "You are a classifier for a hotel‑assistant. "
        "Given the user utterance, respond with exactly ONE of the following "
        "labels (no punctuation, no extra text): "
        "'room_booking', 'hotel_info', 'surroundings', 'unknown'."
    )

    payload = {
        "model_id": model_id,
        "messages": [
            {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
            {"role": "user", "content": [{"type": "text", "text": text}]},
        ],
        "max_tokens": 10,
        "temperature": 0.0,
    }

    # If a project ID is required (e.g., for private deployments), add it
    if project_id:
        payload["project_id"] = project_id

    headers = {
        "Authorization": f"Bearer {iam_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    #print ("-----------------------------------------------------\n")
    #print (f"{headers}")
    #print (payload)
    #print ("-----------------------------------------------------\n")
    resp = requests.post(endpoint, headers=headers, json=payload, timeout=30)
    #print ("-----------------------------------------------------\n")
    #print (f"RESPONSE: {resp.json()}")
    #print ("-----------------------------------------------------\n")

    resp.raise_for_status()
    result = resp.json()
 
    # The response format follows the Watson x AI chat spec:
    #   {"choices": [{"message": {"role":"assistant","content": {"type":"text","text":"room_booking"}}}]}
    try:
        classification = result["choices"][0]["message"]["content"]
        #print ("-----------------------------------------------------\n")
        #print (f"classification: {classification}")
        #print ("-----------------------------------------------------\n")
        classification = classification.strip().lower()

    except Exception as exc:
        raise RuntimeError(f"Unable to extract classification from LLM response: {exc}")

    # Guard against unexpected output
    allowed = {"room_booking", "hotel_info", "surroundings", "unknown"}
    if classification not in allowed:
        raise ValueError(
            f"LLM returned unexpected classification '{classification}'. "
            f"Expected one of {allowed}."
        )
    return classification


# ----------------------------------------------------------------------
# Pre‑invoke plug‑in definition
# ----------------------------------------------------------------------
@tool(
    description="Classify user utterance (room_booking, hotel_info, surroundings) "
                "using Watsonx.ai LLM and prepend the classification as a system "
                "message so downstream tools can react.",
    kind=PythonToolKind.AGENTPREINVOKE,
    expected_credentials=[
        {"app_id": "WATSONX_AI_PLUGIN", "type": ConnectionType.KEY_VALUE}
    ],
)
def classify_user_intent(
    plugin_context: PluginContext,
    agent_pre_invoke_payload: AgentPreInvokePayload,
) -> AgentPreInvokeResult:
    """
    Pre‑invoke plug‑in that:
    1. Reads the last user message from ``agent_pre_invoke_payload``.
    2. Calls Watson x AI (via the /ml/v1/text/chat endpoint) to obtain a
       single‑word intent label.
    3. Inserts a new *system* message containing the label at the beginning of
       the messages list.
    4. Returns ``AgentPreInvokeResult`` with ``continue_processing=True`` and the
       modified payload.

    Environment variables (all required):
        WXO_IAM_URL          – IAM token endpoint (e.g. https://iam.cloud.ibm.com/identity/token)
        WXO_IAM_API_KEY      – API key that has rights to the Watson x AI service
        WXO_WATSONX_URL      – Base URL for Watson x AI (e.g. https://us-south.ml.cloud.ibm.com)
        WXO_WATSONX_MODEL_ID – Model ID to use for classification (e.g. ibm/granite-13b-chat-v2)
        WXO_WATSONX_PROJECT  – (optional) Project ID for private deployments
    """
    # ------------------------------------------------------------------
    # 1️⃣  Pull configuration from the environment
    # ------------------------------------------------------------------
    iam_url = os.getenv("WXO_IAM_URL", "https://iam.cloud.ibm.com/identity/token")
    iam_api_key = os.getenv("WXO_IAM_API_KEY")
    watsonx_base = os.getenv("WXO_WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
    model_id = os.getenv("WXO_WATSONX_MODEL_ID", "meta-llama/llama-3-2-90b-vision-instruct")
    project_id = os.getenv("WXO_WATSONX_PROJECT")  # optional
    if (not _local):
        kv = connections.key_value("WATSONX_AI_PLUGIN")
        iam_api_key = kv.get('IAM_API_KEY', iam_api_key)
        watsonx_base = kv.get("WATSONX_URL", watsonx_base)
        model_id = kv.get("WATSONX_MODEL_ID", model_id)
        project_id = kv.get("WATSONX_PROJECT", project_id)    

    # Basic validation – fail fast if something is missing
    missing = [
        var
        for var, val in {
            "IAM_API_KEY": iam_api_key,
            "WATSONX_URL": watsonx_base,
            "WATSONX_MODEL_ID": model_id,
        }.items()
        if not val
    ]
    if missing:
        raise EnvironmentError(
            f"The following environment variable(s) are required but not set: {', '.join(missing)}"
        )

    # Full endpoint for the chat API
    chat_endpoint = f"{watsonx_base.rstrip('/')}/ml/v1/text/chat?version=2024-10-09"

    # ------------------------------------------------------------------
    # 2️⃣  Extract the last user message
    # ------------------------------------------------------------------
    if not agent_pre_invoke_payload or not agent_pre_invoke_payload.messages:
        # Nothing to classify – just pass through
        result = AgentPreInvokeResult()
        result.continue_processing = True
        result.modified_payload = agent_pre_invoke_payload
        return result

    # The payload may contain multiple messages; the *last* one is the new user input
    user_msg: Message = agent_pre_invoke_payload.messages[-1]
    if not hasattr(user_msg, "content") or not isinstance(user_msg.content, TextContent):
        raise ValueError("User message does not contain text content that can be classified.")

    user_text = user_msg.content.text or ""
    if not user_text.strip():
        # Empty user text – no classification needed
        result = AgentPreInvokeResult()
        result.continue_processing = True
        result.modified_payload = agent_pre_invoke_payload
        return result

    # ------------------------------------------------------------------
    # 3️⃣  Get IAM token and call the LLM
    # ------------------------------------------------------------------
    iam_token = _get_iam_token(iam_api_key, iam_url)
    try:
        intent = _classify_text(
            user_text,
            model_id=model_id,
            project_id=project_id,
            endpoint=chat_endpoint,
            iam_token=iam_token,
        )
    except Exception as exc:
        # If classification fails we still want the conversation to continue,
        # but we add a fallback label.
        intent = "unknown"
        # Optionally you could log the error; here we just embed it in the system
        # message so downstream logic can see what happened.
        error_msg = f"[Classification error: {exc}]"

    # ------------------------------------------------------------------
    # 4️⃣  Build a new system message with the classification
    # ------------------------------------------------------------------
    if intent != "unknown":
        system_text = f"classification:{intent}"
        classification_msg = Message(
            role="user",
            content=TextContent(type="text", text=system_text + "\n" + user_text),
        )

        # Insert the new message at the *front* of the list so downstream agents see it first
        new_payload = agent_pre_invoke_payload.copy(deep=True)
        new_payload.messages.insert(0, classification_msg)
    else:
        new_payload = agent_pre_invoke_payload.copy(deep=True)

    # ------------------------------------------------------------------
    # 5️⃣  Return result
    # ------------------------------------------------------------------
    result = AgentPreInvokeResult()
    result.continue_processing = True
    result.modified_payload = new_payload
    return result


#TESTING LOCALLY

import os
import json
from typing import List

from ibm_watsonx_orchestrate.agent_builder.tools.types import (
    PluginContext,
    GlobalContext,
)

def empty_plugin_context() -> PluginContext:
    """
    Return a PluginContext that satisfies the strict validation rules of the
    current watsonx‑orchestrate SDK.

    Required fields (as of SDK vX.Y):
        global_context.request_id          – any unique string
        global_context.timestamp          – ISO‑8601 timestamp (optional in many
                                            releases, but we include it for safety)

    The function fills those with harmless defaults; the rest of the dicts are
    left empty because the plug‑in does not read them.
    """
    # Minimal but complete GlobalContext
    global_ctx = GlobalContext(
        request_id="demo-request-id",           # any non‑empty string works
        timestamp="1970-01-01T00:00:00Z",        # ISO‑8601 placeholder
        # other optional fields (user, tenant, etc.) are omitted on purpose
    )

    # PluginContext expects both request_context (optional) and global_context
    return PluginContext(
        request_context={},   # empty – we don’t need any user data here
        global_context=global_ctx,
        state={},              # optional, keep empty
        metadata={},           # optional, keep empty
    )

def build_payload(user_text: str) -> AgentPreInvokePayload:
    """
    Build a minimal but fully‑valid AgentPreInvokePayload.
    Required fields (as of the current SDK) are:
        - agent_id   : any non‑empty string that identifies the agent
        - thread_id  : optional, but we provide one for completeness
        - messages   : list of Message objects (at least one user message)
    """
    user_msg = Message(
        role="user",
        content=TextContent(type="text", text=user_text),
    )
    return AgentPreInvokePayload(
        agent_id="demo-agent-id",          # dummy identifier
        thread_id="demo-thread-id",       # optional but nice to have
        messages=[user_msg],
    )

def run_demo(user_text: str) -> List[Message]:
    """
    Executes the plug‑in on a sample user utterance and prints the resulting
    messages (including the injected classification system message).
    """
    # In a real deployment the PluginContext carries metadata; for the demo we
    # can pass an empty stub.
    plugin_ctx = empty_plugin_context()

    payload = build_payload(user_text)

    # Call the plug‑in directly (no Orchestrate runtime needed)
    result = classify_user_intent(plugin_ctx, payload)

    # The plug‑in always sets continue_processing=True, so we can safely read
    # the modified payload.
    modified = result.modified_payload
    return modified.messages


if __name__ == "__main__":

    _local = True

    # Example utterance
    demo_text = "Can I book a double room for next Friday?"
    #demo_text = "Great"

    msgs = run_demo(demo_text)

    print("\n=== Messages after pre‑invoke classification ===")
    for i, m in enumerate(msgs):
        role = m.role
        txt = m.content.text if hasattr(m.content, "text") else "<non‑text>"
        print(f"{i+1}. [{role}] {txt}")


""" COMMANDS;
orchestrate connections add  --app-id WATSONX_AI_PLUGIN 
orchestrate connections configure \
    --app-id WATSONX_AI_PLUGIN \
    --env draft \
    --type team \
    --kind key_value 

orchestrate connections set-credentials \
    --app-id WATSONX_AI_PLUGIN \
    --env draft \
    -e IAM_API_KEY=$WXO_IAM_API_KEY \
    -e WATSONX_URL="https://us-south.ml.cloud.ibm.com" \
    -e WATSONX_MODEL_ID="meta-llama/llama-3-2-90b-vision-instruct" \
    -e WATSONX_PROJECT=$WXO_WATSONX_PROJECT
"""