from smolagents import VLLMModel
from smolagents.tools import Tool
from smolagents.monitoring import TokenUsage
from vllm.transformers_utils.tokenizer import get_tokenizer
from smolagents.models import (
    ChatMessage,
    MessageRole,
    remove_content_after_stop_sequences,

)

from typing import Any

class VLLMModelCustom(VLLMModel):
    def __init__(
        self,
        model_id,
        model_kwargs: dict[str, Any] | None = None,
        apply_chat_template_kwargs: dict[str, Any] | None = None,
        sampling_params=None,
        **kwargs,
    ):
        super().__init__(
            model_id=model_id,
            model_kwargs=model_kwargs,
            apply_chat_template_kwargs=apply_chat_template_kwargs,
            **kwargs
        )
        self.sampling_params = sampling_params

    def generate(
        self,
        messages: list[ChatMessage | dict],
        stop_sequences: list[str] | None = None,
        response_format: dict[str, str] | None = None,
        tools_to_call_from: list[Tool] | None = None,
        **kwargs,
    ) -> ChatMessage:
        from vllm import SamplingParams  # type: ignore
        from vllm.sampling_params import StructuredOutputsParams  # type: ignore

        completion_kwargs = self._prepare_completion_kwargs(
            messages=messages,
            flatten_messages_as_text=(not self._is_vlm),
            stop_sequences=stop_sequences,
            tools_to_call_from=tools_to_call_from,
            **kwargs,
        )

        prepared_stop_sequences = completion_kwargs.pop("stop", [])
        messages = completion_kwargs.pop("messages")
        tools = completion_kwargs.pop("tools", None)
        completion_kwargs.pop("tool_choice", None)

        if not self.sampling_params:
            # Override the OpenAI schema for VLLM compatibility
            structured_outputs = (
                StructuredOutputsParams(json=response_format["json_schema"]["schema"]) if response_format else None
            )


            self.sampling_params = SamplingParams(
                n=kwargs.get("n", 1),
                temperature=kwargs.get("temperature", 0.0),
                max_tokens=kwargs.get("max_tokens", 2048),
                stop=prepared_stop_sequences,
                structured_outputs=structured_outputs,
            )


        prompt = self.tokenizer.apply_chat_template(
            messages,
            tools=tools,
            add_generation_prompt=True,
            tokenize=False,
            **self.apply_chat_template_kwargs,
        )


        out = self.model.generate(
            prompt,
            sampling_params=self.sampling_params,
            **completion_kwargs,
        )

        output_text = out[0].outputs[0].text
        if stop_sequences is not None and not self.supports_stop_parameter:
            output_text = remove_content_after_stop_sequences(output_text, stop_sequences)
        return ChatMessage(
            role=MessageRole.ASSISTANT,
            content=output_text,
            raw={"out": output_text, "completion_kwargs": completion_kwargs},
            token_usage=TokenUsage(
                input_tokens=len(out[0].prompt_token_ids),
                output_tokens=len(out[0].outputs[0].token_ids),
            ),
        )