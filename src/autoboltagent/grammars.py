# grammar that outputs low-fidelity tool call or final_answer
low_fidelity_agent_grammar = r"""
root ::= "<tool_call>\n" payload "\n</tool_call>"
payload ::= fos | final

fos ::= "{\"name\": \"analytical_fos_calculation\", \"arguments\": " fos_args "}}"
fos_args ::= "{" ( num_field ", " dia_field ) | ( dia_field ", " num_field ) "}"
num_field ::= "\"num_bolts\": " int
dia_field ::= "\"bolt_diameter\": " number

final ::= "{\"name\": \"final_answer\", \"arguments\": {\"answer\": " fos_args "}}}"

int ::= digit+
number ::= digit+ frac?
frac ::= "." digit{1,4}

digit ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
"""

# grammar that outputs high-fidelity tool call or final_answer
high_fidelity_agent_grammar = r"""
root ::= "<tool_call>\n" payload "\n</tool_call>"
payload ::= fos | final

fos ::= "{\"name\": \"fea_fos_calculation\", \"arguments\": " fos_args "}}"
fos_args ::= "{" ( num_field ", " dia_field ) | ( dia_field ", " num_field ) "}"
num_field ::= "\"num_bolts\": " int
dia_field ::= "\"bolt_diameter\": " number

final ::= "{\"name\": \"final_answer\", \"arguments\": {\"answer\": " fos_args "}}}"

int ::= digit+
number ::= digit+ frac?
frac ::= "." digit{1,4}

digit ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
"""

# grammar that outputs both types of tool call and final_answer
dual_fidelity_agent_grammar = r"""
root ::= "<tool_call>\n" payload "\n</tool_call>"
payload ::= fos | final

fos ::= "{\"name\": ("\"analytical_fos_calculation\"" | "\"fea_fos_calculation\""), \"arguments\": " fos_args "}}"
fos_args ::= "{" ( num_field ", " dia_field ) | ( dia_field ", " num_field ) "}"
num_field ::= "\"num_bolts\": " int
dia_field ::= "\"bolt_diameter\": " number

final ::= "{\"name\": \"final_answer\", \"arguments\": {\"answer\": " fos_args "}}}"

int ::= digit+
number ::= digit+ frac?
frac ::= "." digit{1,4}

digit ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
"""

low_fidelity_agent_grammar_original = r"""
root ::= "<tool_call>\n" payload "\n</tool_call>"
payload ::= fos | final

fos ::= "{\"name\": \"analytical_fos_calculation\", \"arguments\": " fos_args "}}"
fos_args ::= "{" ( num_field ", " dia_field ) | ( dia_field ", " num_field ) "}"
num_field ::= "\"num_bolts\": " int
dia_field ::= "\"bolt_diameter\": " number

final ::= "{\"name\": \"final_answer\", \"arguments\": {\"answer\": " fos_args "}}"

int ::= digit+
number ::= digit+ frac?
frac ::= "." digit{1,4}

digit ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
"""